package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

var (
	OpCodes = []string{"noop", "set", "clr", "not", "neg", "and", "or", "xor", "add", "sub", "mul", "div", "shl",
		"shr", "cmp", "jmp", "jmpz", "jmpl", "jmpg", "ina", "inx", "outa", "outx", "showf", "show", "hlt"}

	UnaryOpCodes = []string{"noop", "not", "neg", "shl", "shr", "showf", "hlt"}

	BinaryOpCodes = []string{"set", "clr", "and", "or", "xor", "add", "sub", "mul", "div",
		"cmp", "jmp", "jmpz", "jmpl", "jmpg", "ina", "inx", "outa", "outx", "show"}
)

func opcodeHexValue(opcode string) string {
	id := indexOf(OpCodes, opcode)
	return fmt.Sprintf("%02x", id)
}

func contentFromLines(lines []string) string {
	return strings.Join(lines, "\n")
}

func preprocess(sourceFile string) string {
	file, err := os.Open(sourceFile)
	if err != nil {
		fmt.Println("Error opening file:", err)
		os.Exit(1)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	var processedLines []string
	for scanner.Scan() {
		line := strings.ToLower(scanner.Text())
		line = strings.Replace(line, ":", ":\n", -1)
		line = strings.Split(line, "!")[0]
		line = strings.TrimSpace(line)
		if line != "" {
			processedLines = append(processedLines, line)
		}
	}
	return contentFromLines(processedLines)
}

func varsAndInstructions(content string) ([]string, map[string]int, []string) {
	lines := strings.Split(content, "\n")
	vars := []string{}
	labels := make(map[string]int)
	instructions := []string{}

	for _, line := range lines {
		if line == "" {
			continue
		}
		if strings.HasPrefix(line, "@") {
			label := strings.Join(strings.Split(line, ""), "")
			label = label[:len(label)-1]
			if _, exists := labels[label]; !exists {
				labels[label] = len(instructions)
			}
		} else if !strings.HasPrefix(line, "$") {
			instructions = append(instructions, line)
		} else {
			vars = append(vars, line)
		}
	}
	return vars, labels, instructions
}

func validateInstructions(instructions []string, vars, labels []string) bool {
	hexChars := "0123456789abcdefABCDEF"
	binaryChars := "01"

	isValidAddress := func(address, opcode string) bool {
		if opcode == "set" || opcode == "clr" {
			validFlagNumbers := map[string]bool{
				"0": true, "1": true, "2": true, "3": true,
				"#0": true, "#1": true, "#2": true, "#3": true,
				"#d0": true, "#d1": true, "#d2": true, "#d3": true,
				"#h0": true, "#h1": true, "#h2": true, "#h3": true,
			}
			return validFlagNumbers[address]
		}

		if contains(vars, address) || contains(labels, address) {
			return true
		}

		if strings.HasPrefix(address, "#") {
			switch address[1] {
			case 'd':
				_, err := strconv.Atoi(address[2:])
				return err == nil
			case 'h':
				for _, c := range address[2:] {
					if !strings.ContainsRune(hexChars, c) {
						return false
					}
				}
				return true
			case 'b':
				for _, c := range address[2:] {
					if !strings.ContainsRune(binaryChars, c) {
						return false
					}
				}
				return true
			default:
				_, err := strconv.Atoi(address[1:])
				return err == nil
			}
		}

		_, err := strconv.Atoi(address)
		return err == nil
	}

	for _, instruction := range instructions {
		instructionParts := strings.Fields(instruction)
		if len(instructionParts) == 0 {
			fmt.Printf("[ ERROR : Invalid Instruction ] --> '%s'\n", instruction)
			return false
		}

		opcode := instructionParts[0]
		if !contains(OpCodes, opcode) {
			fmt.Printf("[ ERROR : Invalid Instruction ] --> '%s'\n", instruction)
			return false
		}

		if (contains(UnaryOpCodes, opcode) && len(instructionParts) > 1) ||
			(contains(BinaryOpCodes, opcode) && len(instructionParts) < 2) {
			fmt.Printf("[ ERROR : Invalid Instruction ] --> '%s'\n", instruction)
			return false
		}

		address := "0"
		if len(instructionParts) > 1 {
			address = instructionParts[1]
		}

		if !isValidAddress(address, opcode) {
			fmt.Printf("[ ERROR : Invalid Instruction ] --> '%s'\n", instruction)
			return false
		}
	}

	return true
}

func translate(sourceFile, outputFile string) {
	preprocessedData := preprocess(sourceFile)

	vars, labels, instructions := varsAndInstructions(preprocessedData)

	labelsList := keys(labels)
	varsDict := make(map[string]int)
	varsList := []string{}

	for _, v := range vars {
		parts := strings.Split(v, " = ")
		varName := parts[0]
		varValue := "0"
		if len(parts) > 1 {
			varValue = parts[1]
		}

		value := 0
		if strings.HasPrefix(varValue, "#") {
			base := map[byte]int{'d': 10, 'h': 16, 'b': 2}[varValue[1]]
			v, _ := strconv.ParseInt(varValue[2:], base, 0)
			value = int(v)
		} else {
			value, _ = strconv.Atoi(varValue)
		}

		varsDict[varName] = value
		if !contains(varsList, varName) {
			varsList = append(varsList, varName)
		}
	}

	if len(instructions) == 0 || instructions[len(instructions)-1] != "hlt" {
		instructions = append(instructions, "hlt")
	}

	if !validateInstructions(instructions, varsList, labelsList) {
		fmt.Println("Translation Failed!")
		return
	}

	linesWithResolvedAddresses := []string{}
	varInit := len(instructions)

	for _, instruction := range instructions {
		parts := strings.Fields(instruction)
		opcode := parts[0]
		var address string

		if len(parts) > 1 {
			address = parts[1]
		} else {
			address = "0"
		}

		if strings.HasPrefix(address, "#") {
			base := map[byte]int{'d': 10, 'h': 16, 'b': 2}[address[1]]
			v, _ := strconv.ParseInt(address[2:], base, 0)
			address = fmt.Sprintf("%d", v)
		}

		if contains(varsList, address) {
			address = fmt.Sprintf("%d", varInit+indexOf(varsList, address))
		} else if contains(labelsList, address) {
			address = fmt.Sprintf("%d", labels[address])
		}

		addrInt, _ := strconv.Atoi(address)
		opcodeHex := opcodeHexValue(opcode)
		linesWithResolvedAddresses = append(linesWithResolvedAddresses, opcodeHex+fmt.Sprintf("%05x", addrInt))
	}

	for _, varName := range varsList {
		linesWithResolvedAddresses = append(linesWithResolvedAddresses, fmt.Sprintf("%07x", varsDict[varName]))
	}

	ramContent := "v3.0 hex words addressed\n00000: " + strings.Join(linesWithResolvedAddresses, " ")

	file, err := os.Create(outputFile)
	if err != nil {
		fmt.Println("Error creating file:", err)
		os.Exit(1)
	}
	defer file.Close()

	file.WriteString(ramContent)
	fmt.Printf("Translation Successfully Done.\nOutput file: '%s'\n", outputFile)
}

func indexOf(slice []string, item string) int {
	for i, v := range slice {
		if v == item {
			return i
		}
	}
	return -1
}

func contains(slice []string, item string) bool {
	return indexOf(slice, item) != -1
}

func keys(m map[string]int) []string {
	keys := []string{}
	for k := range m {
		keys = append(keys, k)
	}
	return keys
}

func main() {
	if len(os.Args) != 3 {
		fmt.Println("Usage: go run translator.go <source_file> <output_file>")
		return
	}
	sourceFile := os.Args[1]
	outputFile := os.Args[2]
	translate(sourceFile, outputFile)
}
