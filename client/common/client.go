package common

import (
	"fmt"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"
	"bytes"
	"encoding/csv"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

const (
	SUCCESS = 0
	FAIL = 1
	BETS = 2
	NO_MORE_BETS = 3
	CONSULT_WINNER = 4
	WINNERS = 5
)

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID              string
	ServerAddress   string
	LoopAmount      int
	LoopPeriod      time.Duration
	BatchMaxAmount  int
}

// Client Entity that encapsulates how
type Client struct {
	config        ClientConfig
	conn          net.Conn
	amounts_bets  int
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
		amounts_bets: 0,
	}
	return client
}

// SendPackage Send the package controlling no short-writing occurs.
// In case of failure, error is printed in stdout/stderr and exit 1
// is returned
func sendBetPackages(c *Client, betPackages []*BetPackage) error {
	var dataBuffer bytes.Buffer
	dataBuffer.WriteByte(byte(BETS))

	h := NewBetHeader(c.config.ID, fmt.Sprintf("%d", len(betPackages)))
	bbetHeader := h.Serialize()
	dataBuffer.Write(bbetHeader)

	for _, p := range betPackages {
		bbetPackage := p.Serialize()
		dataBuffer.Write(bbetPackage)
	}
	
	data := dataBuffer.Bytes()
	bytesSent := 0
    for bytesSent < len(data) {
        n, err := c.conn.Write(data[bytesSent:])
        if err != nil {
            log.Criticalf(
				"action: send_package | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
        }
        bytesSent += n
    }
	log.Infof(
		"action: send_package | result: success | client_id: %v",
		c.config.ID,
	)
    return nil
}

func expectResponse(c *Client) error {
	var response [1]byte
    _, err := c.conn.Read(response[:])
    if err != nil {
        log.Criticalf(
			"action: receive_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
    }


	log.Infof("action: receive_message | result: success | client_id: %v",
				c.config.ID,
			)
	if response[0] == 0 {
		log.Infof("action: apuesta_enviada | result: success")
	} else {
		log.Infof("action: apuesta_enviada | result: fail")
	}
	c.conn.Close()
    return nil
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Criticalf(
			"action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	log.Infof(
			"action: connect | result: success | client_id: %v",
			c.config.ID,
		)
		return nil
	}

func notifyServer(c *Client) error {
	c.createClientSocket()

	var dataBuffer bytes.Buffer
	dataBuffer.WriteByte(byte(NO_MORE_BETS))

	bid := []byte(c.config.ID)
	bidSize := byte(len(bid))
	dataBuffer.WriteByte(bidSize)
	dataBuffer.Write(bid)

	data := dataBuffer.Bytes()
	bytesSent := 0

	for bytesSent < len(data){
		n, err := c.conn.Write(data[bytesSent:])
		if err != nil {
			log.Criticalf(
				"action: send_package | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
		}
		bytesSent += n
	}

	c.conn.Close()
	return nil
}

func expectWinners(c *Client) error {
	c.createClientSocket()

	var dataBuffer bytes.Buffer
	dataBuffer.WriteByte(byte(CONSULT_WINNER))

	bid := []byte(c.config.ID)
	bidSize := byte(len(bid))
	dataBuffer.WriteByte(bidSize)
	dataBuffer.Write(bid)

	data := dataBuffer.Bytes()
	bytesSent := 0

	for bytesSent < len(data){
		n, err := c.conn.Write(data[bytesSent:])
		if err != nil {
			log.Criticalf(
				"action: send_package | result: fail | client_id: %v | error: %v",
				c.config.ID,
				err,
			)
		}
		bytesSent += n
	}

	var response [2]byte
	_, err := c.conn.Read(response[:])
	if err != nil {
		log.Criticalf(
			"action: receive_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}

	num := response[1]
	log.Infof(
		"action: consulta_ganadores | result: success | cant_ganadores: %v",
		num,
	)

	c.conn.Close()
	return nil
}
	
// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {

	sigChan := make(chan os.Signal, 1) // para manejar las seniales
	signal.Notify(sigChan, syscall.SIGTERM) // para notificar la SIGTERM
	
	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
	filePath := fmt.Sprintf("/dataset/agency-%v.csv", c.config.ID)
	file, err := os.Open(filePath)
	if err != nil {
		log.Criticalf("could not open file %s: %v", filePath, err)
	}
	defer file.Close()
	reader := csv.NewReader(file)

	bets_left := true
	amount_conns := 0
	for bets_left {
		var betPackages []*BetPackage
		
		for msgID := 1; msgID <= c.config.BatchMaxAmount; msgID++ {
			select {
			case <-sigChan:
				// Se recibió la senial SIGTERM, cerrar el cliente de manera graceful
				if c.conn != nil {
					c.conn.Close()
				}
				return
			default:
				// TODO: Modify the send to avoid short-write
				
				record, err := reader.Read()
				if err != nil {
					if err.Error() == "EOF" {
						bets_left = false
						break
						} else {
							log.Criticalf(
								"action: reading_bets | result: fail | client_id: %v | error: %v",
								c.config.ID,
								err,
							)
					}
				}
				
				name := record[0]
				lastname := record[1]
				document := record[2]
				birthday := record[3]
				number := record[4]

				p := NewBetPackage(name, lastname, document, birthday, number)
				betPackages = append(betPackages, p)
			}
		}
		
		if !bets_left && len(betPackages) == 0 {
			break
		}
			
		// Create the connection the server in every loop iteration. Send an
		c.createClientSocket()

		largo := len(betPackages)

		sendBetPackages(c, betPackages)
		expectResponse(c)

		c.amounts_bets += largo
			
		// Wait a time between sending one message and the next one
		time.Sleep(c.config.LoopPeriod)
		amount_conns++
	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)

	notifyServer(c)
	expectWinners(c)
}