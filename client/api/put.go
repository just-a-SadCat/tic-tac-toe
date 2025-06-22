package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"strings"

	"fyne.io/fyne/v2/widget"
)

// AddPlayer sends a PUT request to add a player to a room and returns a confirmation message.
func AddPlayer(roomID, playerID string, statusLabel *widget.Label) (string, error) {
	if roomID == "" || playerID == "" {
		statusLabel.SetText("Error: Please enter both room ID and player ID")
		return "", fmt.Errorf("room ID or player ID is empty")
	}

	// Strip quotes from roomID and playerID
	roomID = strings.Trim(roomID, `"`)
	playerID = strings.Trim(playerID, `"`)

	// Use a struct to safely encode JSON
	payload := struct {
		PlayerID string `json:"player_id"`
	}{PlayerID: playerID}

	data, err := json.Marshal(payload)
	if err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to encode JSON payload: %v", err))
		log.Printf("Failed to encode JSON payload: %v", err)
		return "", fmt.Errorf("failed to encode JSON payload: %w", err)
	}

	url := fmt.Sprintf("http://localhost:8000/rooms/%s/players/add", roomID)

	req, err := http.NewRequest("PUT", url, bytes.NewBuffer(data))
	if err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to create PUT request: %v", err))
		log.Printf("Failed to create PUT request: %v", err)
		return "", fmt.Errorf("failed to create PUT request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to send add player request: %v", err))
		log.Printf("Failed to send add player request: %v", err)
		return "", fmt.Errorf("failed to send add player request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to read response body: %v", err))
		log.Printf("Failed to read response body: %v", err)
		return "", fmt.Errorf("failed to read response body: %w", err)
	}

	if resp.StatusCode == http.StatusOK || resp.StatusCode == http.StatusCreated || resp.StatusCode == http.StatusNoContent {
		confirmation := string(body)
		if resp.StatusCode == http.StatusNoContent {
			confirmation = "Player added successfully" // Default message for 204
		}
		statusLabel.SetText(fmt.Sprintf("Player added to room %s: %s", roomID, confirmation))
		log.Printf("Successfully added player %s to room %s: %s", playerID, roomID, confirmation)
		return confirmation, nil
	}

	err = fmt.Errorf("failed to add player, status: %s, details: %s", resp.Status, string(body))
	statusLabel.SetText(fmt.Sprintf("Error: Failed to add player, Status: %s, Details: %s", resp.Status, string(body)))
	log.Printf("Failed to add player, Status: %s, Details: %s", resp.Status, string(body))
	return "", err
}

// MakePlayPayload represents the JSON payload for the MakePlay endpoint.
type MakePlayPayload struct {
	PlayerID string `json:"player_id"`
	Row      int    `json:"row"`
	Col      int    `json:"col"`
}

// MakePlay sends a PUT request to make a move on the game board and returns the updated board state.
func MakePlay(roomID, playerID string, row, col int, statusLabel *widget.Label) ([][]string, error) {
	if roomID == "" || playerID == "" {
		statusLabel.SetText("Error: Room ID or player ID is empty")
		return nil, fmt.Errorf("room ID or player ID is empty")
	}
	if row < 1 || row > 3 || col < 1 || col > 3 {
		statusLabel.SetText("Error: Row and column must be between 1 and 3")
		return nil, fmt.Errorf("invalid row=%d or col=%d, must be 1-3", row, col)
	}

	payload := MakePlayPayload{
		PlayerID: playerID,
		Row:      row,
		Col:      col,
	}
	data, err := json.Marshal(payload)
	if err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to encode JSON payload: %v", err))
		log.Printf("Failed to encode JSON payload: %v", err)
		return nil, fmt.Errorf("failed to encode JSON payload: %w", err)
	}

	url := fmt.Sprintf("http://localhost:8000/rooms/%s/board", roomID)
	req, err := http.NewRequest("PUT", url, bytes.NewBuffer(data))
	if err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to create PUT request: %v", err))
		log.Printf("Failed to create PUT request: %v", err)
		return nil, fmt.Errorf("failed to create PUT request: %w", err)
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to send make play request: %v", err))
		log.Printf("Failed to send make play request: %v", err)
		return nil, fmt.Errorf("failed to send make play request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to read response body: %v", err))
		log.Printf("Failed to read response body: %v", err)
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusCreated {
		err := fmt.Errorf("failed to make play, status: %s, details: %s", resp.Status, string(body))
		statusLabel.SetText(fmt.Sprintf("Error: Failed to make play, Status: %s, Details: %s", resp.Status, string(body)))
		log.Printf("Failed to make play, Status: %s, Details: %s", resp.Status, string(body))
		return nil, err
	}

	var board [][]string
	if err := json.Unmarshal(body, &board); err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to parse board response: %v", err))
		log.Printf("Failed to parse board response: %v", err)
		return nil, fmt.Errorf("failed to parse board response: %w", err)
	}

	return board, nil
}
