package api

import (
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"

	"fyne.io/fyne/v2/widget"
)

// Player represents a player in the room as returned by the GetPlayers endpoint.
type Player struct {
	PlayerID string `json:"player_id"`
	Name     string `json:"name"`
	Symbol   string `json:"symbol"`
}

// NextTurn represents the FastAPI NextTurn enum ("YES" or "NO").
type NextTurn string

const (
	NextTurnYES NextTurn = "YES"
	NextTurnNO  NextTurn = "NO"
)

// GetPlayers sends a GET request to fetch the list of players in a room.
func GetPlayers(roomID string, statusLabel *widget.Label) ([]Player, error) {
	if roomID == "" {
		statusLabel.SetText("Error: Room ID is empty")
		return nil, fmt.Errorf("room ID is empty")
	}

	url := fmt.Sprintf("http://localhost:8000/rooms/%s/players", roomID)

	resp, err := http.Get(url)
	if err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to send get players request: %v", err))
		log.Printf("Failed to send get players request: %v", err)
		return nil, fmt.Errorf("failed to send get players request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to read response body: %v", err))
		log.Printf("Failed to read response body: %v", err)
		return nil, fmt.Errorf("failed to read response body: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		err := fmt.Errorf("failed to get players, status: %s, details: %s", resp.Status, string(body))
		statusLabel.SetText(fmt.Sprintf("Error: Failed to get players, Status: %s, Details: %s", resp.Status, string(body)))
		log.Printf("Failed to get players, Status: %s, Details: %s", resp.Status, string(body))
		return nil, err
	}

	var players []Player
	if err := json.Unmarshal(body, &players); err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to parse players response: %v", err))
		log.Printf("Failed to parse players response: %v", err)
		return nil, fmt.Errorf("failed to parse players response: %w", err)
	}

	return players, nil
}

// DecideResult sends a GET request to determine the game result, returning "YES", "NO", or a winner UUID.
func DecideResult(roomID string, statusLabel *widget.Label) (string, error) {
	if roomID == "" {
		statusLabel.SetText("Error: Room ID is empty")
		return "", fmt.Errorf("room ID is empty")
	}

	url := fmt.Sprintf("http://localhost:8000/rooms/%s/board", roomID)

	resp, err := http.Get(url)
	if err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to send decide result request: %v", err))
		log.Printf("Failed to send decide result request: %v", err)
		return "", fmt.Errorf("failed to send decide result request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to read response body: %v", err))
		log.Printf("Failed to read response body: %v", err)
		return "", fmt.Errorf("failed to read response body: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		err := fmt.Errorf("failed to decide result, status: %s, details: %s", resp.Status, string(body))
		statusLabel.SetText(fmt.Sprintf("Error: Failed to decide result, Status: %s, Details: %s", resp.Status, string(body)))
		log.Printf("Failed to decide result, Status: %s, Details: %s", resp.Status, string(body))
		return "", err
	}

	// Log raw response for debugging
	log.Printf("Received decide result response: %s", string(body))

	// Parse response as raw JSON to determine type
	var raw json.RawMessage
	if err := json.Unmarshal(body, &raw); err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to parse decide result response: %v", err))
		log.Printf("Failed to parse decide result response: %v", err)
		return "", fmt.Errorf("failed to parse decide result response: %w", err)
	}

	// Check if response is a JSON string (winner UUID)
	if len(raw) > 0 && raw[0] == '"' {
		var winnerID string
		if err := json.Unmarshal(raw, &winnerID); err != nil {
			statusLabel.SetText(fmt.Sprintf("Error: Failed to parse winner ID: %v", err))
			log.Printf("Failed to parse winner ID: %v", err)
			return "", fmt.Errorf("failed to parse winner ID: %w", err)
		}
		log.Printf("Parsed winner ID: %s", winnerID)
		return winnerID, nil
	}

	// Check if response is a JSON object (NextTurn enum)
	if len(raw) > 0 && raw[0] == '{' {
		type NextTurnResponse struct {
			NextTurn string `json:"next_turn"`
		}
		var response NextTurnResponse
		if err := json.Unmarshal(raw, &response); err != nil {
			statusLabel.SetText(fmt.Sprintf("Error: Failed to parse next turn response: %v", err))
			log.Printf("Failed to parse next turn response: %v", err)
			return "", fmt.Errorf("failed to parse next turn response: %w", err)
		}
		if response.NextTurn != "YES" && response.NextTurn != "NO" {
			err := fmt.Errorf("invalid next_turn value: %s", response.NextTurn)
			statusLabel.SetText(fmt.Sprintf("Error: Invalid next_turn value: %s", response.NextTurn))
			log.Printf("Invalid next_turn value: %s", response.NextTurn)
			return "", err
		}
		log.Printf("Parsed next turn: %s", response.NextTurn)
		return response.NextTurn, nil
	}

	err = fmt.Errorf("unexpected response format: %s", string(body))
	statusLabel.SetText(fmt.Sprintf("Error: Unexpected decide result response format"))
	log.Printf("Unexpected response format: %s", string(body))
	return "", err
}
