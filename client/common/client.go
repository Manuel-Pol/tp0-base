package common

import (
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"
	"strconv"

	"github.com/op/go-logging"
)

var log = logging.MustGetLogger("log")

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopAmount    int
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig) *Client {
	client := &Client{
		config: config,
	}
	return client
}

// SendPackage Send the package controlling no short-writing occurs.
// In case of failure, error is printed in stdout/stderr and exit 1
// is returned
func sendPackage(c *Client, p *Package) error {
	data := p.Serialize()
	// ===== responsabilidad de capa de comunicacion =====
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
	// ===== responsabilidad de capa de comunicacion =====
    return nil
}

func expectResponse(c *Client, p *Package) error {
	// ===== responsabilidad de capa de comunicacion =====
	var response [1]byte
    _, err := c.conn.Read(response[:])
    if err != nil {
        log.Criticalf(
			"action: receive_message | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
    }
	// ===== responsabilidad de capa de comunicacion =====


	log.Infof("action: receive_message | result: success | client_id: %v",
				c.config.ID,
			)
	if response[0] == 0 {
		log.Infof("action: apuesta_enviada | result: success | dni: %v | numero: %v",
				p.Document,
				p.Number,
			)
	} else {
		log.Infof("action: apuesta_enviada | result: fail | dni: %v | numero: %v",
				p.Document,
				p.Number,
			)
	}
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
	return nil
}

// StartClientLoop Send messages to the client until some time threshold is met
func (c *Client) StartClientLoop() {

	sigChan := make(chan os.Signal, 1) // para manejar las seniales
	signal.Notify(sigChan, syscall.SIGTERM) // para notificar la SIGTERM
	
	// There is an autoincremental msgID to identify every message sent
	// Messages if the message amount threshold has not been surpassed
	for msgID := 1; msgID <= c.config.LoopAmount; msgID++ {
		select {
		case <-sigChan:
			// Se recibió la senial SIGTERM, cerrar el cliente de manera graceful
			log.Infof("action: shutdown | result: in_progress | client_id: %v", c.config.ID)
			if c.conn != nil {
				c.conn.Close()
			}
			log.Infof("action: shutdown | result: success | client_id: %v", c.config.ID)
			return
		default:
			// Create the connection the server in every loop iteration. Send an
			c.createClientSocket()

			// TODO: Modify the send to avoid short-write
			// hacer el paquete con las variables de entorno
			name := os.Getenv("NOMBRE")
			lastname := os.Getenv("APELLIDO")
			document := os.Getenv("DOCUMENTO")
			birthdayStr := os.Getenv("NACIMIENTO")
			numberStr := os.Getenv("NUMERO")

			birthday64, _ := strconv.ParseUint(birthdayStr, 10, 32)
			// Convertir a uint32
			birthday := uint32(birthday64)

			number64, _ := strconv.ParseUint(numberStr, 10, 16)
			// Convertir a uint16
			number := uint16(number64)

			p := NewPackage(name, lastname, document, birthday, number)
			// mandar el paquete controlando el short-write
			sendPackage(c, p)
			// esperar la confirmación
			// recibir la confirmacion
			// logguear el caso de exito
			expectResponse(c, p)

			// fmt.Fprintf(
			// 	c.conn,
			// 	"[CLIENT %v] Message N°%v\n",
			// 	c.config.ID,
			// 	msgID,
			// )
			// msg, err := bufio.NewReader(c.conn).ReadString('\n')
			// c.conn.Close()

			// if err != nil {
			// 	log.Errorf("action: receive_message | result: fail | client_id: %v | error: %v",
			// 		c.config.ID,
			// 		err,
			// 	)
			// 	return
			// }

			// log.Infof("action: receive_message | result: success | client_id: %v | msg: %v",
			// 	c.config.ID,
			// 	msg,
			// )

			// Wait a time between sending one message and the next one
			time.Sleep(c.config.LoopPeriod)
		}

	}
	log.Infof("action: loop_finished | result: success | client_id: %v", c.config.ID)
}