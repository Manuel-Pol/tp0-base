package common

import (
	"bytes"
	"encoding/binary"
)

const (
	MAX_STR_SIZE_BYTES     = 1
	MAX_IDENTITY_SIZE_BYTES = 4
	MAX_NUMBER_SIZE_BYTES  = 2
)

type Package struct {
	Name      string
	LastName  string
	Document  uint32
	Birthday  string
	Number    uint16
}

func NewPackage(name string, lastname string, birthday string, document uint32, number uint16) *Package {
	return &Package{
		Name:     name,
		LastName: lastname,
		Document: document,
		Birthday: birthday,
		Number:   number,
	}
}

func (p *Package) Serialize() []byte {
	var buffer bytes.Buffer

	bname := []byte(p.Name)
	bnameSize := byte(len(bname))
	buffer.WriteByte(bnameSize)
	buffer.Write(bname)

	blastName := []byte(p.LastName)
	blastNameSize := byte(len(blastName))
	buffer.WriteByte(blastNameSize)
	buffer.Write(blastName)

	binary.Write(&buffer, binary.BigEndian, p.Document)

	bbirthday := []byte(p.Birthday)
	buffer.Write(bbirthday)

	binary.Write(&buffer, binary.BigEndian, p.Number)

	return buffer.Bytes()
}
