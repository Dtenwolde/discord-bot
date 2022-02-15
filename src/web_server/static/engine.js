/*
 * Utility functions
 */

class RollingAverage {
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

function round(number) {
    return Math.round(number * 100) / 100;
}


class DefaultListDict {
    constructor() {
        return new Proxy({}, {
            get: (target, name) => name in target ? target[name] : []
        })
    }
}

/*
 * Renderable objects.
 */
class Point {
    constructor(x, y) {
        this.x = x;
        this.y = y;
    }
}

class Rectangle extends Point {
    constructor(x, y, width, height) {
        super(x, y);
        this.width = width;
        this.height = height;
    }
}

class Circle extends Point {
    constructor(x, y, radius) {
        super(x, y);
        this.radius = radius;
    }
}

class SpriteTile extends Rectangle {
    constructor(image) {
        super(0, 0, 16, 16);
        this.image = "";
        this.setImage(image);
        this.renderable = false;
        this.z = 0;
    }

    render(context) {
        context.drawImage(this.image, this.x, this.y, this.width, this.height);
    }

    setImage(image) {
        if (!(image instanceof Image))
            throw Error("Must give object instanceof class Image.");

        this.image = image;
    }
}

class AnimatedSpriteTile extends SpriteTile {
    constructor(images) {
        if (images.length === 0) throw Error("AnimatedSpriteTile must have at least one image.");
        super(images[0]);

        this.frame = 0;
        this.frameTime = 6; // N ticks per frame
        this.images = images;
    }

    render(context) {
        this.frame = (this.frame + 1) % (this.images.length * this.frameTime);
        this.setImage(this.images[Math.floor(this.frame / this.frameTime)]);
        super.render(context);
    }
}

class CircularCooldown extends Circle {
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
        context.lineWidth = 15;
        context.strokeStyle = this.mainColour;
        context.beginPath();
        context.arc(this.x, this.y, this.radius, 0, 2 * Math.PI);
        context.stroke();

        context.lineWidth = 13;
        context.strokeStyle = this.secondaryColour;
        context.beginPath();
        context.arc(this.x, this.y, this.radius, 0, 2 * Math.PI * this.progress);
        context.stroke();

        if (this.textObject !== null) {
            // TODO: Dont set these properties here.
            this.textObject.fontSize = 25;
            this.textObject.color = "#fff";
            this.textObject.render(context);
        }
    }
}


class ColorTile extends Rectangle {
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

class DrawableText extends Point {
    constructor(x, y) {
        super(x, y);
        this.text = "";
        this.fontSize = 12;
        this.font = "Arial";
        this.color = "#F00";
        this.borderColor = null;
        this.renderable = true;
        this.centered = false;

        this.z = 0;
    }

    render(context) {
        context.font = `${this.fontSize}px ${this.font}`;
        context.fillStyle = this.color;
        context.strokeStyle = this.borderColor;
        context.lineWidth = 0.2;

        this.text.split("\n").map((text, i) => {
            let width = context.measureText(text).width;

            let offset = this.centered ? width / 2 : 0;
            context.fillText(text, this.x - offset, this.y + this.fontSize * .33 + this.fontSize * i);
            if (this.borderColor !== null) {
                context.strokeText(text, this.x - offset, this.y + this.fontSize * .33 + this.fontSize * i);
            }
        });
    }
}

class Button extends Rectangle {
    constructor(x, y, width, height) {
        super(x, y, width, height);
        this.z = 0;
        this.color = "#555";
        this.hoverColor = "#777";
        this.hovering = false;
        this.renderable = true;

        this._onHoverCallbackSet = false;
    }

    setOnHover(canvas) {
        if (!this._onHoverCallbackSet) {
            this._onHoverCallbackSet = true;
            canvas.addEventListener("mousemove", (evt) => {
                const rect = canvas.getBoundingClientRect();
                const scaleX = canvas.width / rect.width;
                const scaleY = canvas.height / rect.height;

                const x = (evt.clientX - rect.left) * scaleX;
                const y = (evt.clientY - rect.top) * scaleY;

                this.hovering = (x > this.x && x < this.x + this.width && y > this.y && y < this.y + this.height);
            });
        }
    }

    setOnClick(canvas, callback) {
        if (!this._onHoverCallbackSet) this.setOnHover(canvas);
        canvas.addEventListener("click", (evt) => {
            if (this.hovering) {
                callback(evt);
            }
        });
    }

    render(context) {
        context.fillStyle = this.hovering ? this.hoverColor : this.color;

        context.fillRect(this.x, this.y, this.width, this.height);
    }
}

/*
 * Main view logic + rendering.
 */
class View {
    constructor(context) {
        this.cameraCenter = new Point(400, 400);

        this.width = 800;
        this.height = 800;
        this.zoom = 1;
        this.context = context;
        this.objects = {};
        this.renderable = true;

        this.children = [];
        this.frametime = 0;
        this.fps = 0;

        this._lastInvokation = 0;
    }

    addChild(child) {
        if (!(child instanceof View))
            throw Error("Must give object instanceof class View.");

        this.children.push(child);
    }

    clearLayer(layer) {
        let l = this.objects[layer];
        if (l === undefined) return;
        this.objects[layer] = undefined;
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
        const index = this.objects[layer].indexOf(object);
        if (index > -1) {
            this.objects[layer] = this.objects[layer].splice(index, 1);
        }
    }

    render() {
        if (!this.renderable) return;

        const start = performance.now();

        const hw = this.width / 2;
        const hh = this.height / 2;
        const xOffset = -this.cameraCenter.x * this.zoom + hw;
        const yOffset = -this.cameraCenter.y * this.zoom + hh;
        this.context.setTransform(this.zoom, 0, 0, this.zoom, xOffset, yOffset);

        const keys = Object.entries(this.objects);
        keys.sort();
        keys.forEach(([key]) => {
            const objects = this.objects[key];
            objects.forEach(obj => {
                if (!obj.renderable) return;

                obj.render(this.context);
            })
        });

        this.context.setTransform(1, 0, 0, 1, 0, 0);
        this.children.forEach(child => {
            child.render()
        });
        this.frametime = (performance.now() - start);

        this.fps = 1000 / (performance.now() - this._lastInvokation);
        this._lastInvokation = performance.now();
    }
}