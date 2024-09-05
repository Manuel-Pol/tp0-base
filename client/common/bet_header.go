package common

import (
	"bytes"
)

type BetHeader struct {
	Agency      string
	AmountBets  string
}

func NewBetHeader(agency string, amountBets string) *BetHeader {
	return &BetHeader{
		Agency:     agency,
		AmountBets: amountBets,
	}
}

func (p *BetHeader) Serialize() []byte {
	var buffer bytes.Buffer

	bagency := []byte(p.Agency)
	bagencySize := byte(len(bagency))
	buffer.WriteByte(bagencySize)
	buffer.Write(bagency)

	bamountBets := []byte(p.AmountBets)
	bamountBetsSize := byte(len(bamountBets))
	buffer.WriteByte(bamountBetsSize)
	buffer.Write(bamountBets)

	return buffer.Bytes()
}
