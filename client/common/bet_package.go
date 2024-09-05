package common

import (
	"bytes"
)

type BetPackage struct {
	Name      string
	LastName  string
	Document  string
	Birthday  string
	Number    string
}

func NewBetPackage(name string, lastname string, document string, birthday string, number string) *BetPackage {
	return &BetPackage{
		Name:     name,
		LastName: lastname,
		Document: document,
		Birthday: birthday,
		Number:   number,
	}
}

func (p *BetPackage) Serialize() []byte {
	var buffer bytes.Buffer

	bname := []byte(p.Name)
	bnameSize := byte(len(bname))
	buffer.WriteByte(bnameSize)
	buffer.Write(bname)

	blastName := []byte(p.LastName)
	blastNameSize := byte(len(blastName))
	buffer.WriteByte(blastNameSize)
	buffer.Write(blastName)

	bdocument := []byte(p.Document)
	bdocumentSize := byte(len(bdocument))
	buffer.WriteByte(bdocumentSize)
	buffer.Write(bdocument)

	bbirthday := []byte(p.Birthday)
	bbirthdaySize := byte(len(bbirthday))
	buffer.WriteByte(bbirthdaySize)
	buffer.Write(bbirthday)

	bnumber := []byte(p.Number)
	bnumberSize := byte(len(bnumber))
	buffer.WriteByte(bnumberSize)
	buffer.Write(bnumber)

	return buffer.Bytes()
}
