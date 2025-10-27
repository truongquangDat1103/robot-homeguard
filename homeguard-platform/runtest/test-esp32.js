const io = require('socket.io-client');

const socket = io('http://localhost:4000', {
    query: {
        type: 'esp32',
        deviceId: 'esp32-test-1'
    }
});

socket.on('connect', () => {
    console.log('✓ ESP32 Connected:', socket.id);

    // Send sensor data every 2 seconds
    setInterval(() => {
        const sensorData = {
            id: `sensor-${Date.now()}`,
            type: 'TEMPERATURE',
            value: 20 + Math.random() * 10,
            unit: '°C',
            timestamp: new Date(),
            deviceId: 'esp32-test-1',
        };

        socket.emit('sensor:data', sensorData);
        console.log('📊 Sent sensor data:', sensorData.value);
    }, 2000);

    // Send robot status every 5 seconds
    setInterval(() => {
        const status = {
            id: 'robot-1',
            state: 'IDLE',
            emotion: 'HAPPY',
            battery: 75 + Math.random() * 20,
            position: { x: 0, y: 0, rotation: 0 },
            isConnected: true,
            lastUpdate: new Date(),
        };

        socket.emit('robot:status', status);
        console.log('🤖 Sent robot status');
    }, 5000);
});

socket.on('robot:command', (cmd) => {
    console.log('📨 Received command:', cmd);
});

socket.on('disconnect', () => {
    console.log('✗ Disconnected');
});