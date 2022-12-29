import {
    Button,
    DrawableText,
    View,
    round,
    SpriteTile,
    ColorTile,
    Point, ScrollableView, CircleLoading,
} from "../engine/engine.js";
import {getUsername} from "../engine/auth.js";
import {HallwayHunters} from "./hallway.js";
import {COLORS, loadImages, TileSet} from "./resources.js";
import {Card} from "./player.js";

let canvas = document.getElementById("canvas");
let context = canvas.getContext("2d");
context.webkitImageSmoothingEnabled = false;
context.mozImageSmoothingEnabled = false;
context.imageSmoothingEnabled = false;

const FPS_INTERVAL = 1000 / 60;

let game;

const view = new View(context, 0, 0, canvas.clientWidth, canvas.clientHeight); // Main wrapper view
view.width = canvas.width;
view.height = canvas.height;
const loadingView = new View(context, 0, 0, canvas.clientWidth, canvas.clientHeight);
const menuView = new View(context, 0, 0, canvas.clientWidth, canvas.clientHeight); // Main menu view
const gameView = new View(context, 0, 0, canvas.clientWidth, canvas.clientHeight); // Game view including UI
view.addChild(gameView);
view.addChild(menuView);
view.addChild(loadingView);
loadingView.renderable = true;
gameView.renderable = false;
menuView.renderable = false;

/*
 * Scrollable card selecting view for the players deck-building
 */
const cardView = new ScrollableView(context, menuView.width * 0.8, 200, menuView.width * 0.1, menuView.height);
const deckView = new ScrollableView(context, menuView.width * 0.9, 200, menuView.width * 0.1, menuView.height);
menuView.addChild(cardView);
menuView.addChild(deckView);


/*
 * In-game UI views etc..
 */
const statsView = new View(context, 0, 0, canvas.clientWidth, canvas.clientHeight); // Informative stats view (fps etc)
const UIView = new View(context, 0, 0, canvas.clientWidth, canvas.clientHeight); // UI View in game, docked at the bottom
const scoreView = new View(context, 0, 0, canvas.clientWidth, canvas.clientHeight); // view for scoreboard
const tileView = new ScrollableView(context, 0, 0, canvas.clientWidth, canvas.clientHeight); // Game view
tileView.zoom = 3;
// The gameView needs a center point to put on the player
tileView.cameraCenter = new Point(0, 0);

gameView.addChild(tileView);
gameView.addChild(UIView);
gameView.addChild(statsView);
gameView.addChild(scoreView);

const TILE_SIZE = 48;
const STATS_INTERVAL = 1000 / 10;
let socket = io("/hallway");


function loadMainContent(gameWrapper) {
    let divs = document.getElementsByClassName("main-content");
    Array.from(divs).forEach((div) => {
        div.style.display = "none";
    });

    document.getElementById(gameWrapper).style.display = "flex";
}


// Game rendering stuff
let then = 0;
let rendering = true;

function gameLoop() {
    if (rendering) requestAnimationFrame(gameLoop);

    const now = performance.now();
    const elapsed = now - then;

    // if enough time has elapsed, draw the next frame

    if (elapsed > FPS_INTERVAL) {

        // Get ready for next frame by setting then=now, but also adjust for your
        // specified fpsInterval not being a multiple of RAF's interval (16.7ms)
        then = now - (elapsed % FPS_INTERVAL);

        // Resizing the canvas should overwrite the width and height variables
        // It has to be a multiple of 2 to remove artifacts around the tilesets
        canvas.width = Math.round(canvas.clientWidth / 2) * 2;
        canvas.height = Math.round(canvas.clientHeight / 2) * 2;

        if (canvas.width !== tileView.width || canvas.height !== tileView.height) {
            tileView.width = canvas.width;
            tileView.height = canvas.height;
        }

        // Clear the canvas and fill with floor tile color.
        context.clearRect(0, 0, canvas.width, canvas.height);
        context.drawImage(game.tileSet.tiles["floor"], 0, 0, canvas.width, canvas.height);

        game.stats.fps.put(gameView.fps);
        game.stats.frameTime.put(gameView.frametime);

        game.statsText.fps.setText(round(game.stats.fps.get()) + " fps");
        game.statsText.stateTime.setText("State update time: " + round(game.stats.stateTime.get()) + " ms");
        game.statsText.ping.setText("Latency: " + round(game.stats.ping.get()) + " ms");
        game.statsText.frameTime.setText("Frame time: " + round(game.stats.frameTime.get()) + " ms");

        // Compute the offset for all tiles, to center rendering on the player.
        try {
            view.render();
        } catch (e) {
            console.log(e);
            rendering = false;
        }
    }
}


function initializeMenu() {
    const x = canvas.clientWidth / 2;

    const buttonWidth = 200;
    const buttonHeight = 50;
    const button = new Button(x - buttonWidth / 2, 600 - buttonHeight / 2, buttonWidth, buttonHeight);
    button.hoverColor = "#5f7791";
    button.color = "#3c5978";
    button.setOnClick(canvas, menuView, () => {
        socket.emit("start", {
            room: ROOM_ID
        });
    });
    button.renderable = true;

    const buttonText = new DrawableText(x, 600);
    buttonText.setText("Start");
    buttonText.fontSize = 25;
    buttonText.color = "rgb(207,226,255)";
    buttonText.centered = true;
    buttonText.z = 1;

    const title = new DrawableText(x, 100);
    title.text = "Hallway Hunters";
    title.fontSize = 45;
    title.color = "rgb(207,226,255)";
    title.borderColor = "#131c2c";
    title.centered = true;

    /*
     * Selectable class buttons for the players
     */
    let blockSize = 80;
    let classButtons = [];
    PLAYER_CLASSES.map((tuple, i) => {
        let cls = tuple[0];
        let info = tuple[1];

        let blockPadding = 20;
        const offset = (PLAYER_CLASSES.length * (blockSize + blockPadding) - blockPadding) / 2 - (blockSize + blockPadding) * i;
        const button = new Button(x - offset, 200, blockSize, blockSize);
        button.hoverColor = "#5f7791";
        button.color = "#3c5978";
        const text = new DrawableText(button.x + blockSize / 2, button.y + blockSize / 2);
        text.color = "rgb(207,226,255)";
        text.setText(cls);
        text.centered = true;

        const infoText = new DrawableText(x, button.y + 100);
        infoText.color = "rgb(207,226,255)";
        infoText.fontSize = 18;
        infoText.setText(info);
        infoText.centered = true;
        infoText.renderable = false;
        button.infoText = infoText;

        classButtons.push(button);
        menuView.addObjects(button, text, infoText);
    });


    classButtons.forEach(clsButton => {
        clsButton.setOnClick(canvas, menuView, () => {
            classButtons.forEach(button => {
                button.color = "#3c5978";
                button.infoText.renderable = false;
            });
            clsButton.color = "#5f7791";
            clsButton.infoText.renderable = true;
        });
    });

    /*
     * Set background image and overlay to grey it out a little
     */
    let background = new SpriteTile(menuView.background);
    // Compute grow factor to ensure no empty edges
    let horizontalGrow = canvas.clientWidth / background.image.width;
    let verticalGrow = canvas.clientHeight / background.image.height;
    let factor = Math.max(horizontalGrow, verticalGrow);
    background.width = background.image.width * factor + 1;
    background.height = background.image.height * factor + 1;

    background.renderable = true;
    let overlay = new ColorTile("#55555555");
    overlay.width = background.width;
    overlay.height = background.height;
    overlay.renderable = true;
    background.z = overlay.z = -1;

    /*
     * Selectable color-buttons for the players to pick their own color
     */
    menuView.colorButtons = {};
    COLORS.map((color, i) => {
        let button = new Button(50, 200 + i * 100, blockSize, blockSize);
        button.hoverColor = "#5f7791";
        button.color = "#3c5978";
        button.text = new DrawableText(button.x + blockSize / 2, button.y + blockSize / 2);
        button.text.color = color;
        button.text.setText(color);
        button.text.fontSize = 15;
        button.text.centered = true;
        button.playerText = new DrawableText(button.x + blockSize + 10, button.y + blockSize / 2);
        button.playerText.fontSize = 20;
        button.playerText.color = "#fff";
        menuView.colorButtons[color] = button;
        button.setOnClick(canvas, menuView,(_) => {
            socket.emit("changeColor", {
                room_id: ROOM_ID,
                color: color,
            });
        });
        menuView.addObjects(button, button.text, button.playerText);
    });

    menuView.addObjects(background, overlay, buttonText, button, title);

    /*
     * Add deckbuilding cardview on the right-hand side of the game
     */
    let cardScrollBackground = new ColorTile("rgba(107,54,39,0.53)");
    cardScrollBackground.x = cardView.x;
    cardScrollBackground.y = cardView.y;
    cardScrollBackground.width = cardView.width;
    cardScrollBackground.height = cardView.height;
    menuView.addObjects(cardScrollBackground);
    let deckScrollBackground = new ColorTile("rgba(107,54,39,0.53)");
    deckScrollBackground.x = deckView.x;
    deckScrollBackground.y = deckView.y;
    deckScrollBackground.width = deckView.width;
    deckScrollBackground.height = deckView.height;
    menuView.addObjects(deckScrollBackground);

    deckView.setOnScroll(canvas, (e) => {
        deckView.viewportOffset.y += Math.sign(e.deltaY) * 40;
    });
    cardView.setOnScroll(canvas, (e) => {
        cardView.viewportOffset.y += Math.sign(e.deltaY) * 40;
    });

    socket.on("deck", (data) => {
        console.log(data);
        createDeckButtons(data);
    });
}

function createDeckButtons(data) {
    cardView.deleteLayer(0, canvas);
    deckView.deleteLayer(0, canvas);

    const p = 4; // Padding
    const w = cardView.width - (p * 2);
    const h = w * 0.4;

    data.remaining_cards.map((data, i) => {
        let count = data[0];
        let card = data[1];
        let name = card.name;


        let cardButton = new Button(p, p + (p + h) * i, w, h);
        cardButton.color = "#694e4e";

        card.name = `${card.name} (${count})`;
        cardButton.card = new Card(cardButton.x, cardButton.y, w, h);
        cardButton.card.setAllText(card);

        cardButton.setOnClick(canvas, cardView,(e) => {
            socket.emit("add_card", {
                room: ROOM_ID,
                card_name: name
            });
        });
        cardView.addObjects(cardButton, cardButton.card);
    });

    data.deck_cards.map((data, i) => {
        let count = data[0];
        let card = data[1];

        let deckButton = new Button(p, p + (p + h) * i, w, h);
        deckButton.color = "#694e4e";
        deckButton.card = new Card(deckButton.x, deckButton.y, w, h);
        deckButton.card.cardName.setText(`${card.name} (${count})`);
        deckButton.card.cardDescription.setText(card.description);

        deckButton.setOnClick(canvas, deckView,(e) => {
            socket.emit("remove_card", {
                room: ROOM_ID,
                card_name: card.name
            });
        });
        deckView.addObjects(deckButton, deckButton.card);
    });
}

function initializeLoading() {
    let background = new SpriteTile(menuView.background);
    background.renderable = true;
    background.width = menuView.background.width;
    background.height = menuView.background.height;
    let overlay = new ColorTile("#55555555");
    overlay.renderable = true;
    overlay.width = background.width;
    overlay.height = background.height;
    background.z = overlay.z = -1;



    const circleLoading = new CircleLoading(background.width / 2, background.height / 2, 35);
    loadingView.infoText = new DrawableText(background.width / 2, background.height / 2 + 100);
    loadingView.infoText.color = "#ffffff";
    loadingView.infoText.fontSize = 20;
    loadingView.infoText.centered = true;
    loadingView.addObjects(background, overlay, circleLoading, loadingView.infoText);
}

function updateScoreboard() {
    scoreView.deleteLayer(0, canvas);
    let sorted_score = [];
    Object.values(game.players).forEach(player => {
        sorted_score.push([player, player.score])
    });

    sorted_score.sort(function (a, b) {
        return a[1] - b[1];
    });

    sorted_score.map((player, i) => {
        player[0].scoreText.x = canvas.width - 100;
        player[0].scoreText.y = canvas.height - i * player[0].scoreText.fontSize - 50;
        scoreView.addObjects(player[0].scoreText);
    })
}

function postStartInitialize(data) {
    updateScoreboard();

    tileView.setOnScroll(canvas, (e) => {
        tileView.zoom += Math.sign(e.deltaY) * -0.5;
        tileView.zoom = Math.max(Math.min(tileView.zoom, 4), 1)
    });
}

let intervalID;
let started = false;

function start() {
    intervalID = requestAnimationFrame(gameLoop);

    game.initializePlayers();
    game.initializeCards();
    game.initializeEnemies();

    // Initialize player sprites
    for (let key in game.players) {
        if (game.players.hasOwnProperty(key)) {
            game.players[key].renderable = true;
            game.players[key].z = 3;
            tileView.addObjects(game.players[key]);
        }
    }

    // Setup stats view
    statsView.addObjects(
        game.statsText.frameTime,
        game.statsText.fps,
        game.statsText.ping,
        game.statsText.stateTime
    );


    /*
     * Register all socket.io functions to the game object.
     */
    socket.on("game_state", (data) => {
        if (!data.started) {
            // Lobby information
            COLORS.forEach(color => {
                menuView.colorButtons[color].playerText.setText("");
            });
            data.all_players.forEach(player => {
                menuView.colorButtons[player.color].playerText.setText(player.username);
                menuView.colorButtons[player.color].playerText.color = player.state === 3 ? "#fff" : "#494";
            });
        } else {
            game.setState(data);

            if (!started) {
                postStartInitialize(data);
                started = true;
            }
            updateScoreboard();
        }
    });


    // Request game state on initialization.
    socket.emit("game_state", {
        "room": ROOM_ID
    });

    loadingView.renderable = false;
    menuView.renderable = true;
}

function onCardClick(i, evt) {
    sendAction(String(i));
}

function initialize(tileSet) {
    game = new HallwayHunters(tileView, UIView, tileSet, onCardClick);

    initializeLoading();
    initializeMenu();

    socket.on("message", (data) => {
        console.log(data);
    });

    socket.on("join", (data) => {
        console.log(`${data} joined the room.`);
        start();
    });
    let startTime;

    setInterval(function () {
        startTime = Date.now();
        socket.emit('ping');
    }, STATS_INTERVAL);


    socket.on('pong', function () {
        game.stats.ping.put(Date.now() - startTime);
    });

    // Keylisteners for user input
    document.addEventListener("keydown", (ev) => {
        const VALID_ACTIONS = [
            "Enter", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"
        ];
        if (VALID_ACTIONS.indexOf(ev.key) !== -1) {
            sendAction(ev.key);
        }
    });

}

function sendAction(action) {
    let data = {
        room: ROOM_ID,
        action: action
    };
    socket.emit("action", data);
}

socket.on("loading", (data) => {
    loadingView.infoText.setText(data);
    menuView.renderable = false;
    loadingView.renderable = true;
});

socket.on("start", () => {
    loadingView.renderable = false;
    gameView.renderable = true;
});


function changeSettings() {
    let data = {
        room_id: ROOM_ID,
        settings: {}
    };
    socket.emit("change settings", data)
}

socket.on("set_session", (data) => {
    USER_NAME = data;
    // Load resources

    let tileSet = new TileSet();
    let setBackground = (image) => {
        menuView.background = image
    };
    loadImages("/static/images/tiles/dungeon_sheet.png", (x) => tileSet.splitTileset(x)).then(() =>
    loadImages("/static/images/tiles/background.png", setBackground).then(() => {
        initialize(tileSet);

        // Emit join event for server to register user
        socket.emit("join", {
            "room": ROOM_ID,
        });
    }));
});

// Start the game
socket.emit("set_session", {username: getUsername()});


