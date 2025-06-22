package main

import (
	"fmt"
	"log"
	"strings"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/widget"
	"github.com/google/uuid"
	"github.com/just-a-SadCat/client/api"
)

func main() {
	myApp := app.New()
	myWindow := myApp.NewWindow("Start menu")
	idPlayer := ""
	idRoom := ""

	// Status label for errors and game state
	statusLabel := widget.NewLabel("")

	// Define containers at top level
	startContent := container.NewVBox()
	roomContent := container.NewVBox()
	inputSecondPlayerID := widget.NewEntry()
	inputSecondPlayerID.SetPlaceHolder("Podaj ID drugiego gracza")

	// Start menu inputs
	inputName := widget.NewEntry()
	inputName.SetPlaceHolder("Podaj nazwę gracza do utworzenia")
	inputPlayerID := widget.NewEntry()
	inputPlayerID.SetPlaceHolder("Podaj ID gracza do utworzenia pokoju")
	inputRoomID := widget.NewEntry()
	inputRoomID.SetPlaceHolder("Podaj ID pokoju do dołączenia")

	// Populate startContent
	startContent.Objects = []fyne.CanvasObject{
		inputName,
		widget.NewButton("Zapisz gracza", func() {
			playerName := inputName.Text
			idPlayer = api.CreatePlayer(playerName, statusLabel)
			if idPlayer != "" {
				inputPlayerID.SetText(idPlayer) // Pre-fill player ID input
			}
		}),
		inputPlayerID,
		widget.NewButton("Utwórz pokój", func() {
			playerID := inputPlayerID.Text
			idRoom = api.CreateRoom(playerID, statusLabel)
			if idRoom != "" {
				inputRoomID.SetText(idRoom) // Pre-fill room ID input
				log.Printf("Room created with ID: %s", idRoom)
			}
		}),
		inputRoomID,
		widget.NewButton("Dołącz do pokoju", func() {
			roomID := strings.Trim(inputRoomID.Text, `"`) // Remove quotes from roomID
			if roomID == "" {
				statusLabel.SetText("Error: Please enter a room ID")
				log.Println("Room ID is empty")
				return
			}
			// Update room view content
			roomContent.Objects = []fyne.CanvasObject{
				widget.NewLabel(fmt.Sprintf("Pokój: %s", roomID)),
				inputSecondPlayerID,
				widget.NewButton("Dodaj drugiego gracza", func() {
					secondPlayerID := strings.Trim(inputSecondPlayerID.Text, `"`) // Remove quotes from playerID
					confirmation, err := api.AddPlayer(roomID, secondPlayerID, statusLabel)
					if err != nil {
						log.Printf("Error adding second player: %v", err)
						return
					}
					log.Printf("Second player added to room %s: %s", roomID, confirmation)
				}),
				widget.NewButton("Rozpocznij grę", func() {
					players, err := api.GetPlayers(roomID, statusLabel)
					if err != nil {
						log.Printf("Error fetching players: %v", err)
						return
					}
					if len(players) != 2 {
						statusLabel.SetText("Error: Two players are required to start the game")
						log.Printf("Invalid number of players: %d", len(players))
						return
					}
					// Game view with 3x3 grid, active player, and turn switching
					activePlayerIndex := 0 // Start with first player
					activePlayerLabel := widget.NewLabel(fmt.Sprintf("Current player: %s (%s)", players[activePlayerIndex].Name, players[activePlayerIndex].Symbol))

					// Create 3x3 grid of buttons
					grid := container.NewGridWithColumns(3)
					buttons := make([]*widget.Button, 9)
					for i := 0; i < 9; i++ {
						btn := widget.NewButton("", func() {})
						btn.Resize(fyne.NewSize(60, 60)) // Square buttons
						btnIndex := i                    // Capture index for closure
						btn.OnTapped = func() {
							// Clear status before move
							statusLabel.SetText("")
							// Map button index to 1-based row and col
							row := btnIndex/3 + 1
							col := btnIndex%3 + 1
							// Send move to server
							board, err := api.MakePlay(roomID, players[activePlayerIndex].PlayerID, row, col, statusLabel)
							if err != nil {
								log.Printf("Error making play: %v", err)
								return
							}
							// Sync board with response
							for r := 0; r < 3; r++ {
								for c := 0; c < 3; c++ {
									idx := r*3 + c
									buttons[idx].SetText(board[r][c])
									if board[r][c] != " " {
										buttons[idx].Disable()
									}
								}
							}
							// Log board state for debugging
							log.Printf("Board state: %v", board)
							log.Printf("Placed %s at button %d (row=%d, col=%d) by %s", players[activePlayerIndex].Symbol, btnIndex, row, col, players[activePlayerIndex].Name)

							// Check game result
							result, err := api.DecideResult(roomID, statusLabel)
							if err != nil {
								log.Printf("Error deciding result: %v", err)
								return
							}

							switch result {
							case "YES":
								// NextTurn.YES: Continue game
								// Switch to the other player
								activePlayerIndex = (activePlayerIndex + 1) % 2
								activePlayerLabel.SetText(fmt.Sprintf("Current player: %s (%s)", players[activePlayerIndex].Name, players[activePlayerIndex].Symbol))
								log.Printf("Switched to player: %s (%s)", players[activePlayerIndex].Name, players[activePlayerIndex].Symbol)
							case "NO":
								// Stalemate
								statusLabel.SetText("Stalemate: No winner!")
								log.Printf("Game ended: Stalemate")
								// Disable all buttons
								for _, btn := range buttons {
									btn.Disable()
								}
							default:
								// Validate result as UUID
								if _, err := uuid.Parse(result); err != nil {
									statusLabel.SetText("Error: Invalid winner ID format")
									log.Printf("Invalid winner ID format: %s, error: %v", result, err)
									return
								}
								// Winner found
								winnerName := "Unknown"
								for _, p := range players {
									if p.PlayerID == result {
										winnerName = p.Name
										break
									}
								}
								statusLabel.SetText(fmt.Sprintf("Winner: %s!", winnerName))
								log.Printf("Game ended: Winner is %s (ID: %s)", winnerName, result)
								// Disable all buttons
								for _, btn := range buttons {
									btn.Disable()
								}
							}
						}
						buttons[i] = btn
						grid.Add(btn)
					}

					// Game view content
					gameContent := container.NewVBox(
						widget.NewLabel("Gra w kółko i krzyżyk"),
						activePlayerLabel,
						grid,
						widget.NewButton("Powrót", func() {
							// Return to room view
							myWindow.SetContent(roomContent)
						}),
						statusLabel,
					)
					myWindow.SetContent(gameContent)
				}),
				widget.NewButton("Powrót", func() {
					// Return to start menu
					myWindow.SetContent(startContent)
				}),
				statusLabel,
			}
			myWindow.SetContent(roomContent)
		}),
		statusLabel,
	}

	myWindow.SetContent(startContent)
	myWindow.ShowAndRun()
}
