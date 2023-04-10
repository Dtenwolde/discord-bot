import {
    DrawableText,
    RollingAverage,
    Point,
    Rectangle,
    ColorTile,
    SpriteTile,
    DirectionalAnimatedSpriteTile,
    AnimatedSpriteTile,
    CircularCooldown,
    FadingText
} from "../engine/engine.js";
import {COLORS} from "./resources.js";
import {Card, CARDBACK_COLOR, CARDBACK_SELECTED_COLOR, DAMAGE_COLOR, Player} from "./player.js";


export class HallwayHunters {
    constructor(view, UIView, tileSet, callback) {
        this.view = view;
        this.UIView = UIView;
        this.tileSet = tileSet;
        this.cards = [];
        this.enemySprites = [];
        this.entities = [];
        this.cardCallback = callback;
    }

    state = {
        board_size: 30,
        all_players: [],
        player_data: {
            dead: false,
            name: "",
            class_name: "",
            position: {
                x: 0,
                y: 0
            },
            previous_position: {
                x: 0,
                y: 0
            },
            pre_move: {
                x: 0,
                y: 0
            },
            is_moving: false,
            movement_cooldown: 0,
            movement_timer: 0,
            movement_queue: [],
            ability_cooldown: 0,
            ability_timer: 0,
            sprint_cooldown: 0,
            sprint_timer: 0,
            stored_items: [{
                name: "",
            }],
            passives: [{
                name: "",
                time: 0,
                total_time: 0,
                uid: ""
            }],
            camera_list: []
        },
        visible_tiles: [
            {x: 0, y: 0, tile: {}}
        ],
        board: [],

    };

    stats = {
        ping: new RollingAverage(5),
        stateTime: new RollingAverage(5),
        fps: new RollingAverage(5),
        frameTime: new RollingAverage(5)
    };
    statsText = {
        ping: new DrawableText(5, 5),
        fps: new DrawableText(5, 5 + 12),
        stateTime: new DrawableText(5, 5 + 24),
        frameTime: new DrawableText(5, 5 + 36),
    };
    notification = new FadingText(0, 0);
    lookup = {};
    items = [];

    players = {};
    passives = {};

    setState(data) {
        let start = performance.now();
        if (this.state.board.length === 0) {
            this.initializeBoard(data.board_size);
        }

        data.removed_entity_ids.forEach(entityId => {
            this.entities[entityId].renderable = false;
            delete this.entities[entityId];
        });

        if (data.visible_tiles !== undefined) {
            this.updateBoardSprites(data.visible_tiles);
            this.updateItems(data.visible_tiles);
        }

        this.state = {
            ...this.state,
            ...data
        };

        this.setPassives()

        // This marks the tiles which are visible
        this.lookup = {};
        this.state.visible_tiles.forEach((obj) => {
            if (this.lookup[obj.x] === undefined) {
                this.lookup[obj.x] = {};
            }
            this.lookup[obj.x][obj.y] = true;
        });

        // Fix renderable players like this.
        for (const player of Object.values(this.players)) {
            player.renderable = false;
        }

        // Update player objects
        data.all_players.forEach(player => {
            this.players[player.color].renderable = true;
            this.players[player.color].update(player);
        });

        data.visible_entities.forEach(entity => {
            if (entity.sprite_name === undefined) return;
            let entityObj = this.entities[entity.uid];

            if (entityObj === undefined) {
                let src = this.tileSet.tiles[entity.sprite_name];
                if (src === undefined) {
                    throw "Invalid sprite name received from server: " + entity.sprite_name;
                }
                entityObj = new SpriteTile(src);
                entityObj.z = 4;
                this.view.addObjects(entityObj);
                this.entities[entity.uid] = entityObj;
            }
            if (entityObj.image !== this.tileSet.tiles[entity.sprite_name]) {
                entityObj.setImage(this.tileSet.tiles[entity.sprite_name]);
            }
            entityObj.zoom = entity.zoom;
            entityObj.renderable = true;
            entityObj.x = entity.position.x * 16;
            entityObj.y = entity.position.y * 16;
            entityObj.orientation = entity.direction;
        });

        const readyStates = ["Ready", "Processing...", "Not Ready"]
        let sum = new Point(0, 0);
        this.state.all_players.forEach(player => {
            const p = this.players[player.color];
            p.score = player.stored_items.length;
            p.scoreText.text = player.username + " " + readyStates[p.data.ready];

            if (!player.dead) {
                sum.x += player.position.x;
                sum.y += player.position.y;
            }
        });

        /*
         * Render card logic
         * First disable all cards renderability, followed by updating every card with the new value and setting the
         *  renderability to true for all cards which you have.
         */

        this.cards.forEach(card => {
            card.renderable = false;
        });
        this.state.player_data.hand.forEach((card, index) => {
            let cardObject = this.cards[index];
            cardObject.setAllText(card);
            cardObject.damage.colour = DAMAGE_COLOR[card.damage_type];
            cardObject.renderable = true;
            // cardObject.cardName.text = card.name;
        })

        // Update new camera center based on average position between all players
        let newCameraCenter = new Point(
            sum.x / this.state.all_players.length * 16,
            sum.y / this.state.all_players.length * 16
        );

        // Camera center as own player location
        // let newCameraCenter = new Point(data.player_data.position.x * 16, data.player_data.position.y * 16);
        if (this.state.started)
            this.updateRenderable(this.view.cameraCenter, newCameraCenter);

        this.view.cameraCenter = newCameraCenter;

        this.stats.stateTime.put(performance.now() - start);
    };

    setPassives() {
        /*
         * Remove passives from UI which are no longer active.
         */
        Object.keys(this.passives).forEach((uid) => {
            let found = false;
            for (let i = 0; i < this.state.player_data.passives.length; i++) {
                if (uid === this.state.player_data.passives[i].uid) {
                    found = true;
                }
            }
            if (!found) {
                this.UIView.removeObject(this.passives[uid]);
            }
        });

        /*
         * Set player passive renderable objects.
         */
        this.state.player_data.passives.map((p, i) => {
            const radius = 20;
            const padding = 4;
            const width = radius * 3 + padding;
            let passiveObj = this.passives[p.uid];
            if (passiveObj === undefined) {
                passiveObj = new CircularCooldown(200 + width * i, 30 + width, radius);
                passiveObj.textObject.setText(p.name);
                this.passives[p.uid] = passiveObj;
                this.UIView.addObjects(passiveObj);
            }
            passiveObj.progress = p.time / p.total_time;
        });
    }

    updateBoardSprites(tiles) {
        tiles.forEach(obj => {
            let oldTile = this.state.board[obj.x][obj.y];
            oldTile.setImage(this.tileSet.tiles[obj.tile.image])
        });
    }

    updateRenderable(oldCenter, newCenter) {
        const w = this.view.width / this.view.zoom;
        const h = this.view.height / this.view.zoom;
        const coordScale = 16;
        const oldRenderbox = new Rectangle(oldCenter.x - w / 2 - coordScale, oldCenter.y - h / 2 - coordScale, w + 32, h + 32);
        const newRenderbox = new Rectangle(newCenter.x - w / 2 - coordScale, newCenter.y - h / 2 - coordScale, w + 32, h + 32);

        [oldRenderbox, newRenderbox].forEach(e => {
            e.x = Math.max(Math.floor(e.x / coordScale), 0);
            e.y = Math.max(Math.floor(e.y / coordScale), 0);
            e.width = Math.ceil(e.width / coordScale);
            e.height = Math.ceil(e.height / coordScale);
        });

        // Remove the renderable property from the old box
        let width = Math.min(oldRenderbox.x + oldRenderbox.width, this.state.board_size);
        let height = Math.min(oldRenderbox.y + oldRenderbox.height, this.state.board_size);
        for (let x = oldRenderbox.x; x < width; x++) {
            for (let y = oldRenderbox.y; y < height; y++) {
                this.state.board[x][y].renderable = false;
            }
        }
        // Add the renderable property to the new box
        width = Math.min(newRenderbox.x + newRenderbox.width, this.state.board_size);
        height = Math.min(newRenderbox.y + newRenderbox.height, this.state.board_size);

        // TODO: Dont recompute the entire vision lines every new data update
        const FOG_Z = 100;
        this.view.deleteLayer(FOG_Z, canvas);
        for (let x = newRenderbox.x; x < width; x++) {
            for (let y = newRenderbox.y; y < height; y++) {
                this.state.board[x][y].renderable = true;

                if (this.lookup[x] === undefined || !this.lookup[x][y]) {
                    let tile = new ColorTile("rgba(0,0,0,0.2)");
                    tile.x = x * 16;
                    tile.y = y * 16;
                    tile.z = FOG_Z;
                    tile.renderable = true;

                    this.view.addObjects(tile);
                }
            }
        }
    }


    updateItems(tiles) {
        tiles.forEach(tile => {
            if (this.state.board[tile.x][tile.y].item !== undefined) {
                if (tile.tile.item === null) {
                    // TODO: Remove this object from the renderable list
                    this.state.board[tile.x][tile.y].item.renderable = false;
                    this.state.board[tile.x][tile.y].item = undefined;
                } else {
                    this.state.board[tile.x][tile.y].item.setImage(this.tileSet.tiles[tile.tile.item.name]);
                }
                return;
            }
            if (tile.tile.item !== null) {
                let item = new SpriteTile(this.tileSet.tiles[tile.tile.item.name]);
                // FIXME: Items aren't always renderable, update this.
                item.renderable = true;
                item.x = tile.x * 16;
                item.y = tile.y * 16;
                item.z = 1;
                this.state.board[tile.x][tile.y].item = item;
                this.view.addObjects(item);
            }
        });
    }

    initializeUI() {
        this.notification.x = this.UIView.width / 2;
        this.notification.y = this.UIView.height / 3;
        this.notification.centered = true;
        this.notification.width = this.UIView.width / 2;
        this.notification.fontSize = 36;
        this.notification.fadeThreshold = 60 * 2;
        this.notification.fadeTicks = 60 * 5;
        this.notification.color = "#8bd0dc";
        this.notification.borderColor = "#000";

        this.UIView.addObjects(this.notification);
    }

    initializeBoard(board_size) {
        for (let x = 0; x < board_size; x++) {
            let list = [];
            for (let y = 0; y < board_size; y++) {
                let sprite = new SpriteTile(this.tileSet.tiles["void"]);
                sprite.x = x * 16;
                sprite.y = y * 16;
                list.push(sprite);
                this.view.addObjects(sprite);
            }
            this.state.board.push(list);
        }
    }

    initializeCards() {
        const MAX_HAND_CARDS = 8;
        // Set cards in hand information
        for (let i = 0; i < MAX_HAND_CARDS; i++) {
            const w = 100;
            const h = 144;
            const padding = 4;
            let card = new Card(padding + i * (w + padding), this.view.height - h + padding, w, h);
            card.cardBack.setOnClick(canvas, this.UIView, (evt) => {
                // Reset color for all cards except for the selected one
                this.cards.forEach(card => card.cardBack.color = CARDBACK_COLOR);
                card.cardBack.color = CARDBACK_SELECTED_COLOR;
                this.cardCallback(i, evt);
            });
            this.cards.push(card);
            this.UIView.addObjects(this.cards[i]);
        }
    }

    /*
     * This function should get called when the game has started, and we know how many player entities need to be rendered
     */
    initializePlayers() {
        COLORS.forEach(colour => {
            let player = new Player(
                this.view,
                this.tileSet,
                colour
            );
            [0, 90, 180, 270].forEach(d => {
                player.setWalkingAnimation(d, [
                    this.tileSet.tiles[`${colour}_${d}_0`],
                    this.tileSet.tiles[`${colour}_${d}_1`],
                    this.tileSet.tiles[`${colour}_${d}_0`],
                    this.tileSet.tiles[`${colour}_${d}_2`],
                ]);

                player.setIdleAnimation(d, [
                    this.tileSet.tiles[`${colour}_${d}_0`]
                ]);
            });
            this.players[colour] = player;
        });
    }

    /*
     * This function should get called to initialize all animatedspritetiles for the enemies
     */
    initializeEnemies() {
        let directionLists = [];
        ["north", "east", "south", "west"].forEach(d => {
            directionLists.push([
                this.tileSet.tiles[`slime_${d}_0`],
                this.tileSet.tiles[`slime_${d}_1`],
                this.tileSet.tiles[`slime_${d}_0`],
                this.tileSet.tiles[`slime_${d}_2`],
            ])
        });
        this.enemySprites["slime"] = new DirectionalAnimatedSpriteTile(
            directionLists[0],
            directionLists[1],
            directionLists[2],
            directionLists[3]
        );
    }
}