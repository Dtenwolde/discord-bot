/*
 * Utility functions
 */
export let keyState = {};

export class RollingAverage {
    constructor(n) {
        this.values = [];
        this.n = n;
    }

    put(value) {
        this.values.unshift(value);
        this.values = this.values.slice(0, this.n);
    }

    get() {
        return this.values.reduce((a, b) => a + b, 0) / this.values.length;
    }
}

export function round(number) {
    return Math.round(number * 100) / 100;
}


/*
 * Renderable objects.
 */
export class Point {
    constructor(x, y) {
        this.x = x;
        this.y = y;
    }
}

export class Rectangle extends Point {
    constructor(x, y, width, height) {
        super(x, y);
        this.width = width;
        this.height = height;
    }
}

export class Circle extends Point {
    constructor(x, y, radius) {
        super(x, y);
        this.radius = radius;
    }
}

export class SpriteTile extends Rectangle {
    constructor(image) {
        super(0, 0, 16, 16);
        this.image = "";
        this.setImage(image);
        this.renderable = false;
        this.zoom = 1;
        this.z = 0;
    }

    render(context) {
        let x = this.x - (this.width * (this.zoom - 1)) / 2;
        let y = this.y - (this.height * (this.zoom - 1)) / 2;
        context.drawImage(this.image, x, y, this.width * this.zoom, this.height * this.zoom);
    }

    setImage(image) {
        if (!(image instanceof Image))
            throw Error("Must give object instanceof class Image.");

        this.image = image;
    }
}

export class AnimatedSpriteTile extends SpriteTile {
    constructor(images, optionalArgs) {
        if (images.length === 0) throw Error("AnimatedSpriteTile must have at least one image.");
        super(images[0]);

        this.frame = 0;
        this.frameTime = 6; // N ticks per frame
        this.images = images;
        this.loop = true;

        this.zooms = undefined;

        if (optionalArgs !== undefined) {
            // Zoom per frame is optionally defined
            if (optionalArgs.zooms !== undefined) {
                this.zooms = optionalArgs.zooms;
            }
            if (optionalArgs.loop !== undefined) {
                this.loop = optionalArgs.loop;
            }
        }
    }

    render(context) {
        if (!this.loop && this.frame + 1 === this.images.length * this.frameTime) {
            // If we aren't looping the animation, stop rendering this sprite.
            // TODO: Delete this object from the sprite manager
            console.log("Not looping")
            return;
        }

        this.frame = (this.frame + 1) % (this.images.length * this.frameTime);
        // TODO: Merge this class with AnimatedDirectionalSpriteTile
        let frame_idx = Math.floor(this.frame / this.frameTime);

        let b = {x: this.x, y: this.y, width: this.width, height: this.height};

        if (this.zooms !== undefined) {
            this.width *= this.zooms[frame_idx];
            this.height *= this.zooms[frame_idx];
            this.x -= (this.width - b.width) / 2;
            this.y -= (this.height - b.height) / 2;
        }

        this.setImage(this.images[frame_idx]);
        super.render(context);

        this.x = b.x;
        this.y = b.y;
        this.width = b.width;
        this.height = b.height;
    }
}


export class DirectionalAnimatedSpriteTile extends SpriteTile {
    constructor(imN, imE, imS, imW, optionalArgs) {
        for (let im in [imN, imE, imS, imW]) {
            if (im.length === 0) throw Error("All orientation animations must have at least one image.");
        }
        super(imS[0]);

        this.orientations = {
            0: new AnimatedSpriteTile(imN),
            90: new AnimatedSpriteTile(imE),
            180: new AnimatedSpriteTile(imS),
            270: new AnimatedSpriteTile(imW),
        };

        // TODO: Pass this to all orientations
        this.frame = 0;
        this.frameTime = 6; // N ticks per frame
        this.orientation = 180;
        this.zooms = undefined;

        if (optionalArgs !== undefined) {
            // Zoom per frame is optionally defined
            if (optionalArgs.zooms !== undefined) {
                this.zooms = optionalArgs.zooms;
            }
        }
    }

    render(context) {
        let currentAnimation = this.orientations[this.orientation];

        this.frame = (this.frame + 1) % (currentAnimation.images.length * this.frameTime);
        let frame_idx = Math.floor(this.frame / this.frameTime);

        let b = {x: this.x, y: this.y, width: this.width, height: this.height};

        if (this.zooms !== undefined) {
            this.width *= this.zooms[frame_idx];
            this.height *= this.zooms[frame_idx];
            this.x -= (this.width - b.width) / 2;
            this.y -= (this.height - b.height) / 2;
        }

        this.setImage(currentAnimation.images[frame_idx]);

        super.render(context);

        this.x = b.x;
        this.y = b.y;
        this.width = b.width;
        this.height = b.height;
    }
}

export class FilledCircle extends Circle {
    constructor(x, y, radius) {
        super(x, y, radius);
        this.color = "#418eb0";

        this.renderable = true;

        this.textObject = new DrawableText(x, y);
        this.textObject.color = "#fff";
        this.textObject.centered = true;
        this.textObject.renderable = true;

        this.z = 0;
    }

    render(context) {
        context.fillStyle = this.color;
        context.beginPath();
        context.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
        context.fill();

        if (this.textObject !== null) {
            // TODO: Dont set these properties here.
            this.textObject.fontSize = this.radius * 1.2;
            this.textObject.x = this.x;
            this.textObject.y = this.y;
            this.textObject.render(context);
        }
    }
}

export class CircularCooldown extends Circle {
    /*
     * The progress property defines how far the cooldown is along.
     * Range is 0-1.
     */
    constructor(x, y, radius) {
        super(x, y, radius);
        this.progress = 0;
        this.mainColour = "#418eb0";
        this.secondaryColour = "#3f3656";

        this.renderable = true;
        this.textObject = new DrawableText(x, y);
        this.textObject.centered = true;

        this.z = 0;
    }

    render(context) {
        context.lineWidth = this.radius * 0.6;
        context.strokeStyle = this.mainColour;
        context.beginPath();
        context.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
        context.stroke();

        context.lineWidth = this.radius * 0.4;
        context.strokeStyle = this.secondaryColour;
        context.beginPath();
        context.arc(this.x, this.y, this.radius, 0, 2 * Math.PI * this.progress);
        context.stroke();

        if (this.textObject !== null) {
            // TODO: Dont set these properties here.
            this.textObject.fontSize = this.radius * 0.75;
            this.textObject.color = "#fff";
            this.textObject.x = this.x;
            this.textObject.y = this.y;
            this.textObject.render(context);
        }
    }
}


export class ColorTile extends Rectangle {
    constructor(color) {
        super(0, 0, 16, 16);
        this.color = color;

        this.z = 0;
        this.renderable = true;
    }

    render(context) {
        context.fillStyle = this.color;
        context.fillRect(this.x, this.y, this.width, this.height);
    }
}

/**
 * Uses canvas.measureText to compute and return the width of the given text of given font in pixels.
 *
 * @param {String} text The text to be rendered.
 * @param {String} font The css font descriptor that text is to be rendered with (e.g. "bold 14px verdana").
 *
 * @see https://stackoverflow.com/questions/118241/calculate-text-width-with-javascript/21015393#21015393
 */
function getTextWidth(text, font) {
    // re-use canvas object for better performance
    const canvas = getTextWidth.canvas || (getTextWidth.canvas = document.createElement("canvas"));
    const context = canvas.getContext("2d");
    context.font = font;
    const metrics = context.measureText(text);
    return metrics.width;
}

export class CircleLoading extends Point {
    constructor(x, y, radius) {
        super(x, y);
        this.renderable = true;
        this.z = 2;
        this.radius = radius;
        this.tick = 0;
        this.chasing = true;
        this.ticksPerRotation = 180;
        this.chaseSpeed = 2.4;
    }

    render(context) {
        const phi = (2 * Math.PI);
        this.tick++;

        if (this.tick % (this.ticksPerRotation / this.chaseSpeed) === 0) this.chasing = !this.chasing;

        const a1 = (this.tick % this.ticksPerRotation) / this.ticksPerRotation * phi;
        const a2 = (a1 + ((this.tick * this.chaseSpeed) % this.ticksPerRotation) / this.ticksPerRotation * phi) % (phi);

        let sAngle, eAngle;
        if (this.chasing) {
            sAngle = a1;
            eAngle = a2;
        } else {
            sAngle = a2;
            eAngle = a1;
        }
        context.lineWidth = 15;
        context.strokeStyle = this.mainColour;
        context.beginPath();
        context.arc(this.x, this.y, this.radius, sAngle, eAngle);
        context.stroke();
    }
}

export class DrawableText extends Point {
    constructor(x, y) {
        super(x, y);
        this._lines = [];
        this.fontSize = 12;
        this.font = "Arial";
        this.color = "#F00";
        this.borderColor = null;
        this.renderable = true;
        this.centered = false;
        this.width = Infinity;  // Default DrawableText has no overflow
        this.height = Infinity;  // Default DrawableText has no overflow
        this.z = 0;
    }

    setText(newText) {
        if (this.width === 0)
            return;

        const words = newText.split(' ');
        this._lines = [];

        let currentLine = words[0];
        let currentLineWidth = getTextWidth(currentLine, `${this.fontSize}px ${this.font}`);
        let spaceWidth = getTextWidth(" ", `${this.fontSize}px ${this.font}`);

        words.slice(1).forEach(word => {
            const wordWidth = getTextWidth(word, `${this.fontSize}px ${this.font}`);
            const width = wordWidth + spaceWidth;

            if (currentLineWidth + width >= this.width) {
                // This word made the line break, store previous words as line and go next.
                this._lines.push(currentLine);
                currentLine = word;
                currentLineWidth = wordWidth;
            } else {
                currentLine += " " + word;
                currentLineWidth += width;
            }
        });
        this._lines.push(currentLine);
    }

    render(context) {
        context.font = `${this.fontSize}px ${this.font}`;
        context.fillStyle = this.color;
        context.strokeStyle = this.borderColor;
        context.lineWidth = 0.2;

        this._lines.map((text, i) => {
            let width = context.measureText(text).width;
            let offset = this.centered ? width / 2.0 : 0;
            let height = this.fontSize * .33 + this.fontSize * i;

            if (height + this.fontSize * 1.33 > this.height) return;

            context.fillText(text, this.x - offset, this.y + height);
            if (this.borderColor !== null) {
                context.strokeText(text, this.x - offset, this.y + this.fontSize * .33 + this.fontSize * i);
            }
        });
    }
}

export class Button extends Rectangle {
    constructor(x, y, width, height) {
        super(x, y, width, height);
        this.z = 0;
        this.color = "#555";
        this.hoverColor = "#777";
        this.hovering = undefined;
        this.renderable = true;
        this.onMove = undefined;
        this.onClick = undefined;
    }

    setOnHover(canvas, view) {
        if (this.onMove !== undefined)
            return;

        this.onMove = (evt) => {
            const res = view.calculateRenderingOffset()
            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;

            const x = (evt.clientX - rect.left) * scaleX - res.xOffset;
            const y = (evt.clientY - rect.top) * scaleY - res.yOffset;
            this.hovering = (x > this.x && x < this.x + this.width && y > this.y && y < this.y + this.height);
        }

        canvas.addEventListener("mousemove", this.onMove);
    }


    setOnClick(canvas, view, callback) {
        if (this.onMove === undefined) this.setOnHover(canvas, view);

        this.onClick = (evt) => {
            // We can be hovering over a button without having moved first
            if (this.hovering === undefined) {
                this.onMove(evt);
            }

            if (this.hovering) {
                callback(evt);
            }
        };

        canvas.addEventListener("click", this.onClick);
    }

    delete(canvas) {
        if (this.onClick !== undefined) {
            canvas.removeEventListener("click", this.onClick);
        }
        if (this.onMove !== undefined) {
            canvas.removeEventListener("mousemove", this.onMove)
        }
    }

    render(context) {
        context.fillStyle = this.hovering ? this.hoverColor : this.color;

        context.fillRect(this.x, this.y, this.width, this.height);
    }
}


/*
 * Main view logic + rendering.
 */
export class View {
    constructor(context, x, y, width, height) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.cameraCenter = undefined;
        this.viewportOffset = undefined;
        this.zoom = 1;
        this.context = context;
        this.objects = {};
        this.renderable = true;

        this.children = [];
        this.frametime = 0;
        this.fps = 0;

        this._lastInvokation = 0;
        this.parent = undefined;
    }

    addChild(child) {
        if (!(child instanceof View))
            throw Error("Must give object instanceof class View.");

        child.parent = this;
        this.children.push(child);
    }

    deleteLayer(layer, canvas) {
        let l = this.objects[layer];
        if (l === undefined) return;

        this.objects[layer].forEach(obj => {
            if (obj instanceof Button)
                obj.delete(canvas);
        });

        delete this.objects[layer];
    }

    addObjects() {
        Array.prototype.slice.call(arguments).forEach(object => {
            let l = this.objects[object.z];
            if (l === undefined) {
                this.objects[object.z] = l = [];
            }
            l.push(object);
        });
    }

    removeObject(object, layer) {
        if (layer === undefined) {
            layer = object.z;
        }
        const index = this.objects[layer].indexOf(object);
        if (index > -1) {
            this.objects[layer].splice(index, 1);
        }
    }

    calculateRenderingOffset() {
        let xOffset = 0;
        let yOffset = 0;


        // cameraCenter works on zoom level, whereas coordinates and width work on view level
        xOffset += this.x;
        yOffset += this.y;

        let centerMod = {
            x: 0,
            y: 0
        }
        if (this.cameraCenter !== undefined) {
            const hw = this.width / 2;
            const hh = this.height / 2;
            xOffset -= this.cameraCenter.x * this.zoom - hw;
            yOffset -= this.cameraCenter.y * this.zoom - hh;
            centerMod.x += this.cameraCenter.x - hw;
            centerMod.y += this.cameraCenter.y - hh;
        }
        if (this.viewportOffset !== undefined) {
            xOffset -= this.viewportOffset.x;
            yOffset -= this.viewportOffset.y;
            centerMod.x += this.viewportOffset.x;
            centerMod.y += this.viewportOffset.y;
        }

        if (this.parent !== undefined) {
            const res = this.parent.calculateRenderingOffset();
            xOffset += res.xOffset;
            yOffset += res.yOffset;
        }

        return {xOffset, yOffset, centerMod};
    }

    render() {
        if (!this.renderable) return;
        const start = performance.now();

        const res = this.calculateRenderingOffset();
        const xOffset = res.xOffset;
        const yOffset = res.yOffset;
        const centerMod = res.centerMod;

        let viewportBounds = {
            x1: centerMod.x,
            x2: this.width + centerMod.x,
            y1: centerMod.y,
            y2: this.height + centerMod.y
        }
        this.context.setTransform(this.zoom, 0, 0, this.zoom, xOffset, yOffset);

        const keys = Object.entries(this.objects);
        keys.sort();
        keys.forEach(([key]) => {
            const objects = this.objects[key];
            objects.forEach(obj => {
                // Programmatically turn off renderability
                if (!obj.renderable) return;

                // Check if this object is within the viewport
                if (obj.x + obj.width < viewportBounds.x1
                    || obj.x > viewportBounds.x2
                    || obj.y + obj.height < viewportBounds.y1
                    || obj.y > viewportBounds.y2
                ) {
                    return;
                }
                obj.render(this.context);
            })
        });

        this.context.setTransform(1, 0, 0, 1, 0, 0);
        this.children.forEach(child => {
            child.render(this.x, this.y)
        });
        this.frametime = (performance.now() - start);

        this.fps = 1000 / (performance.now() - this._lastInvokation);
        this._lastInvokation = performance.now();
    }
}


export class ScrollableView extends View {
    constructor(context, x, y, width, height) {
        super(context, x, y, width, height);

        this.viewportOffset = new Point(0, 0);
    }

    setOnScroll(canvas, callback) {
        canvas.addEventListener("wheel", (evt) => {
            if (!this.renderable) return;

            const rect = canvas.getBoundingClientRect();
            const scaleX = canvas.width / rect.width;
            const scaleY = canvas.height / rect.height;
            const x = (evt.clientX - rect.left) * scaleX;
            const y = (evt.clientY - rect.top) * scaleY;
            const mouseOver = (x > this.x && x < this.x + this.width && y > this.y && y < this.y + this.height);

            if (mouseOver) {
                callback(evt);
            }
        });
    }
}


document.addEventListener("keydown", (ev) => {
    keyState[ev.key] = true;
});
document.addEventListener("keyup", (ev) => {
    keyState[ev.key] = false;
});