class EyeTrackingApp {
    constructor() {
        this.video = document.getElementById("video-feed");
        this.canvas = document.getElementById("gaze-overlay");
        this.ctx = this.canvas.getContext("2d");
        this.heatmapInstance = h337.create({ container: document.getElementById("heatmap-canvas") });
        this.gazeData = [];
        this.isTracking = false;

        this.initializeWebSocket();
        this.initializeEventListeners();
        this.initializeCamera();
    }

    initializeWebSocket() {
        this.socket = new WebSocket("ws://localhost:5000/ws");
        this.socket.onopen = () => this.updateConnectionStatus(true);
        this.socket.onclose = () => this.updateConnectionStatus(false);
        this.socket.onerror = () => this.updateConnectionStatus(false);
        this.socket.onmessage = (event) => this.handleGazeData(JSON.parse(event.data));
    }

    handleGazeData(data) {
        if (!this.isTracking) return;
        this.gazeData.push(data);
        this.updateGazeVisualization(data);
        this.updateHeatmap(data);
    }

    updateGazeVisualization(data) {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctx.fillStyle = "rgba(255, 0, 0, 0.6)";
        this.ctx.beginPath();
        this.ctx.arc(data.x, data.y, 10, 0, Math.PI * 2);
        this.ctx.fill();
    }

    updateHeatmap(data) {
        this.heatmapInstance.addData({ x: data.x, y: data.y, value: 1 });
    }

    async initializeCamera() {
        const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: "user" } });
        this.video.srcObject = stream;
    }

    initializeEventListeners() {
        document.getElementById("start-tracking").addEventListener("click", () => this.isTracking = true);
        document.getElementById("stop-tracking").addEventListener("click", () => this.isTracking = false);
    }
}

window.onload = () => new EyeTrackingApp();
