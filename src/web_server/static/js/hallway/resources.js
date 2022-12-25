export const COLORS = ["blue", "red", "green", "purple", "black"];


function rotateImageData(context, imageData, degrees) {
    // Copy input image to create place to generate new image to.
    let output = context.createImageData(imageData.width, imageData.height);

    let w = imageData.width;
    let h = imageData.height;
    let center = {x: w / 2, y: h / 2};

    let radians = (degrees * Math.PI / 180);
    for (let x = 0; x < w; x++) {
        for (let y = 0; y < h; y++) {
            // Compute vector angle and size
            let vx = x - center.x;
            let vy = y - center.y;
            let angle = Math.atan2(vx, vy) + radians;
            let size = Math.sqrt(vx * vx + vy * vy);

            // Compute new position of pixel.
            let newY = Math.sin(angle) * size + center.x;
            let newX = Math.cos(angle) * size + center.y;

            for (let c = 0; c < 4; c++) {
                output.data[Math.round((newY * w + newX) * 4 + c)] = imageData.data[Math.round((y * w + x) * 4 + c)];
            }
        }
    }
    return output;
}

export class TileSet {
    constructor() {
    }

    tiles = {};

    splitTileset(tileSet) {
        let canvas = document.createElement("canvas");
        canvas.className = "disable-anti-aliasing";
        canvas.width = tileSet.width * 3;
        canvas.height = tileSet.height * 3;
        let context = canvas.getContext("2d");

        context.clearRect(0, 0, canvas.width, canvas.height);
        context.webkitImageSmoothingEnabled = false;
        context.mozImageSmoothingEnabled = false;
        context.imageSmoothingEnabled = false;

        context.scale(3, 3);
        context.drawImage(tileSet, 0, 0);

        const S = 48;

        this.tiles["edge_b"] = context.getImageData(6 * S, S, S, S);
        this.tiles["edge_b_top"] = context.getImageData(6 * S, 0, S, S);
        this.tiles["edge_b_alt1"] = context.getImageData(8 * S, 5 * S, S, S);
        this.tiles["edge_b_alt1_top"] = context.getImageData(8 * S, 4 * S, S, S);
        this.tiles["edge_b_alt2"] = context.getImageData(9 * S, 5 * S, S, S);
        this.tiles["edge_b_alt2_top"] = context.getImageData(9 * S, 4 * S, S, S);
        this.tiles["edge_b_alt3"] = context.getImageData(5 * S, 4 * S, S, S);

        this.tiles["corner_br"] = context.getImageData(9 * S, 3 * S, S, S);
        this.tiles["corner_br_top"] = context.getImageData(9 * S, 2 * S, S, S);

        this.tiles["corner_bl"] = context.getImageData(8 * S, 3 * S, S, S);
        this.tiles["corner_bl_top"] = context.getImageData(8 * S, 2 * S, S, S);

        this.tiles["corner_tr"] = context.getImageData(9 * S, S, S, S);
        this.tiles["corner_tr_top"] = context.getImageData(9 * S, 0, S, S);

        this.tiles["corner_tl"] = context.getImageData(8 * S, S, S, S);
        this.tiles["corner_tl_top"] = context.getImageData(8 * S, 0, S, S);

        this.tiles["inner_corner_br"] = context.getImageData(7 * S, 3 * S, S, S);
        this.tiles["inner_corner_br_top"] = context.getImageData(7 * S, 2 * S, S, S);

        this.tiles["inner_corner_bl"] = context.getImageData(5 * S, 3 * S, S, S);
        this.tiles["inner_corner_bl_top"] = context.getImageData(5 * S, 2 * S, S, S);

        this.tiles["inner_corner_tr"] = context.getImageData(7 * S, S, S, S);
        this.tiles["inner_corner_tr_top"] = context.getImageData(7 * S, 0, S, S);

        this.tiles["inner_corner_tl"] = context.getImageData(5 * S, S, S, S);
        this.tiles["inner_corner_tl_top"] = context.getImageData(5 * S, 0, S, S);

        this.tiles["totem_top_left"] = context.getImageData(10 * S, 0, S, S);
        this.tiles["totem_mid_left"] = context.getImageData(10 * S, S, S, S);
        this.tiles["totem_bot_left"] = context.getImageData(10 * S, 2 * S, S, S);
        this.tiles["totem_top_right"] = context.getImageData(11 * S, 0, S, S);
        this.tiles["totem_mid_right"] = context.getImageData(11 * S, S, S, S);
        this.tiles["totem_bot_right"] = context.getImageData(11 * S, 2 * S, S, S);

        this.tiles["edge_t"] = context.getImageData(6 * S, 3 * S, S, S);
        this.tiles["edge_t_alt1"] = context.getImageData(7 * S, 5 * S, S, S);

        this.tiles["edge_l"] = context.getImageData(7 * S, 2 * S, S, S);
        this.tiles["edge_l_alt1"] = context.getImageData(6 * S, 4 * S, S, S);
        this.tiles["edge_l_alt2"] = context.getImageData(7 * S, 4 * S, S, S);

        this.tiles["edge_r"] = context.getImageData(5 * S, 2 * S, S, S);
        this.tiles["void"] = context.getImageData(S, S, S, S);
        this.tiles["edge_t"] = context.getImageData(6 * S, 3 * S, S, S);

        this.tiles["floor"] = context.getImageData(6 * S, 2 * S, S, S);
        this.tiles["wall_test"] = context.getImageData(6 * S, S, S, S);

        this.tiles["ladder"] = context.getImageData(15 * S, 8 * S, S, S);
        this.tiles["camera"] = context.getImageData(7 * S, 6 * S, S, S);

        this.tiles["UI_corner_bl"] = context.getImageData(19 * S, 11 * S, S, S);
        this.tiles["UI_edge_left"] = context.getImageData(20 * S, 11 * S, S, S);
        this.tiles["UI_edge_bottom"] = context.getImageData(21 * S, 11 * S, S, S);

        this.tiles["thin_wall_vcb"] = context.getImageData(17 * S, 16 * S, S, S);
        this.tiles["thin_wall_v"] = context.getImageData(18 * S, 16 * S, S, S);
        this.tiles["thin_wall_vct1"] = context.getImageData(19 * S, 16 * S, S, S);
        this.tiles["thin_wall_vct2"] = context.getImageData(20 * S, 16 * S, S, S);

        this.tiles["key_0"] = context.getImageData(21 * S, 16 * S, S, S);
        this.tiles["key_1"] = context.getImageData(22 * S, 16 * S, S, S);
        this.tiles["key_2"] = context.getImageData(23 * S, 16 * S, S, S);
        this.tiles["key_3"] = context.getImageData(24 * S, 16 * S, S, S);

        this.tiles["thin_wall_hcr1"] = context.getImageData(17 * S, 17 * S, S, S);
        this.tiles["thin_wall_h"] = context.getImageData(18 * S, 17 * S, S, S);
        this.tiles["thin_wall_hcl1"] = context.getImageData(19 * S, 17 * S, S, S);
        this.tiles["thin_wall_hcl2"] = context.getImageData(20 * S, 17 * S, S, S);
        this.tiles["thin_wall_hcr2"] = context.getImageData(21 * S, 17 * S, S, S);

        ["v", "h"].forEach((o, y) => {
            for (let i = 0; i < 4; i++) {
                this.tiles[`door_${o}_${i}`] = context.getImageData((13 + i) * S, (16 + y) * S, S, S);
            }
        });

        COLORS.map((color, row) => {
            for (let i = 0; i < 3; i++) {
                this.tiles[color + "_90_" + i] = context.getImageData(i * S, (11 + row) * S, S, S);
                this.tiles[color + "_270_" + i] = context.getImageData((i + 3) * S, (11 + row) * S, S, S);
                this.tiles[color + "_180_" + i] = context.getImageData((i + 6) * S, (11 + row) * S, S, S);
                this.tiles[color + "_0_" + i] = context.getImageData((i + 9) * S, (11 + row) * S, S, S);
            }
            this.tiles[color + "_dead"] = context.getImageData(12 * S, (11 + row) * S, S, S);

            // Base chest sprite without animation
            this.tiles["chest_" + color] = context.getImageData(13 * S, (11 + row) * S, S, S);
            for (let i = 0; i < 6; i++) {
                this.tiles["chest_" + color + "_" + i] = context.getImageData((i + 13) * S, (11 + row) * S, S, S);
            }
        });

        COLORS.map((color, i) => {
            this.tiles["collector_" + color] = context.getImageData((19 + i) * S, 6 * S, S, S);
        });

        for (let i = 0; i < 4; i++) {
            this.tiles["rubbish_" + i] = context.getImageData((i + 15) * S, 7 * S, S, S);
        }

        // Load all enemies into the tiles object
        for (let i = 0; i < 3; i++) {
            this.tiles["slime_east_" + i] = context.getImageData(i * S, 16 * S, S, S);
            this.tiles["slime_west_" + i] = context.getImageData((i + 3) * S, 16 * S, S, S);
            this.tiles["slime_south_" + i] = context.getImageData((i + 6) * S, 16 * S, S, S);
            this.tiles["slime_north_" + i] = context.getImageData((i + 9) * S, 16 * S, S, S);
        }
        ["ru", "ld"].map((direction, y) => {
            for (let i = 0; i < 7; i++) {
                this.tiles[`monkeyball_${i}_${direction}`] = context.getImageData(i * S, (17 + y) * S, S, S);
            }
        });
        for (let i = 0; i < 8; i++) {
            this.tiles[`sloth_${i}`] = context.getImageData(i * S, 19 * S, S, S);
        }

        // Load all spells into the tiles object
        for (let i = 0; i < 2; i++) {
            let data = context.getImageData((19 + i) * S, 12 * S, S, S);
            this.tiles["spear_270_" + i] = data;
            this.tiles["spear_0_" + i] = rotateImageData(context, data, 0);
            this.tiles["spear_90_" + i] = rotateImageData(context, data, 90);
            this.tiles["spear_180_" + i] = rotateImageData(context, data, 180);
        }
        // Axe animation is a rotation
        for (let i = 0; i < 4; i++) {
            this.tiles["axe_270_" + i] = context.getImageData((21 + i) * S, 12 * S, S, S);
            this.tiles["axe_0_" + i] = context.getImageData((21 + i) * S, 12 * S, S, S);
            this.tiles["axe_90_" + i] = context.getImageData((21 + i) * S, 13 * S, S, S);
            this.tiles["axe_180_" + i] = context.getImageData((21 + i) * S, 13 * S, S, S);
        }
        // Heal animation takes 5 unique frames, last one is repeated and zoomed in multiple times
        // Heal has no rotation
        for (let i = 0; i < 5; i++) {
            this.tiles["heal_" + i] = context.getImageData((19 + i) * S, 14 * S, S, S);
        }


        // Load all images into canvas to be used later
        for (const [title, data] of Object.entries(this.tiles)) {
            canvas.width = data.width;
            canvas.height = data.height;
            context.putImageData(data, 0, 0);

            let image = new Image();
            image.src = canvas.toDataURL();
            this.tiles[title] = image;
        }

        console.log("Done loading images.");
    }
}


export async function loadImages(src, callback) {
    return new Promise((resolve, reject) => {
        let image = new Image();
        image.onload = () => {
            callback(image);
            resolve();
        };
        image.onerror = reject;
        image.src = src;
    });
}
