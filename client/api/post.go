package api

import (
	"bytes"
	"fmt"
	"io"
	"log"
	"net/http"

	"fyne.io/fyne/v2/widget"
)

func CreatePlayer(playerName string, statusLabel *widget.Label) string {
	if playerName == "" {
		statusLabel.SetText("Error: Please enter a player name")
		return ""
	}

	data := []byte(fmt.Sprintf(`{"name": "%s"}`, playerName))
	url := "http://localhost:8000/players"

	resp, err := http.Post(url, "application/json", bytes.NewBuffer(data))
	if err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to send request: %v", err))
		log.Printf("Failed to send POST request: %v", err)
		return ""
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to read response body: %v", err))
		log.Printf("Failed to read response body: %v", err)
		return ""
	}

	if resp.StatusCode == http.StatusOK || resp.StatusCode == http.StatusCreated {
		statusLabel.SetText(fmt.Sprintf("Player created successfully! Player ID: %s", string(body)))
		log.Printf("Successfully created player: %s, Player ID: %s", playerName, string(body))
		return string(body)
	} else {
		statusLabel.SetText(fmt.Sprintf("Error: Server responded with status: %s, Details: %s", resp.Status, string(body)))
		log.Printf("Server responded with status: %s, Details: %s", resp.Status, string(body))
		return ""
	}
}

func CreateRoom(playerID string, statusLabel *widget.Label) string {
	if playerID == "" {
		statusLabel.SetText("Error: Please enter a player ID")
		return ""
	}

	data := []byte(fmt.Sprintf(`{"player_id": %s}`, playerID))
	url := "http://localhost:8000/rooms"

	resp, err := http.Post(url, "application/json", bytes.NewBuffer(data))
	if err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to send create room request: %v", err))
		log.Printf("Failed to send create room request: %v", err)
		return ""
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		statusLabel.SetText(fmt.Sprintf("Error: Failed to read response body: %v", err))
		log.Printf("Failed to read response body: %v", err)
		return ""
	}

	if resp.StatusCode == http.StatusOK || resp.StatusCode == http.StatusCreated {
		roomID := string(body)
		statusLabel.SetText(fmt.Sprintf("Room created successfully! Room ID: %s", roomID))
		log.Printf("Successfully created room for player ID: %s, Room ID: %s", playerID, roomID)
		return roomID
	} else {
		statusLabel.SetText(fmt.Sprintf("Error: Server responded with status: %s, Details: %s", resp.Status, string(body)))
		log.Printf("Server responded with status: %s, Details: %s", resp.Status, string(body))
		return ""
	}
}
