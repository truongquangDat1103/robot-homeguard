-- ============================================
-- Robot Pet HomeGuard Database Schema
-- Database: PostgreSQL 15+
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- USERS & AUTHENTICATION
-- ============================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    avatar_url TEXT,
    role VARCHAR(50) DEFAULT 'user' CHECK (role IN ('admin', 'user', 'guest')),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(500) UNIQUE NOT NULL,
    refresh_token VARCHAR(500),
    device_info JSONB,
    ip_address INET,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(token);

-- ============================================
-- ROBOT DEVICES
-- ============================================

CREATE TABLE robots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    model VARCHAR(100),
    firmware_version VARCHAR(50),
    owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(50) DEFAULT 'offline' CHECK (status IN ('online', 'offline', 'sleep', 'error')),
    location VARCHAR(255),
    last_seen_at TIMESTAMP WITH TIME ZONE,
    configuration JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_robots_device_id ON robots(device_id);
CREATE INDEX idx_robots_owner_id ON robots(owner_id);
CREATE INDEX idx_robots_status ON robots(status);

-- ============================================
-- SENSOR DATA
-- ============================================

CREATE TABLE sensor_data (
    id BIGSERIAL PRIMARY KEY,
    robot_id UUID REFERENCES robots(id) ON DELETE CASCADE,
    sensor_type VARCHAR(50) NOT NULL CHECK (sensor_type IN 
        ('temperature', 'humidity', 'gas', 'flame', 'motion', 'ultrasonic', 'sound', 'light')),
    sensor_name VARCHAR(100),
    value NUMERIC(10, 2),
    unit VARCHAR(20),
    raw_data JSONB,
    threshold_exceeded BOOLEAN DEFAULT false,
    alert_level VARCHAR(20) CHECK (alert_level IN ('normal', 'warning', 'danger', 'critical')),
    location VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sensor_data_robot_id ON sensor_data(robot_id);
CREATE INDEX idx_sensor_data_sensor_type ON sensor_data(sensor_type);
CREATE INDEX idx_sensor_data_timestamp ON sensor_data(timestamp DESC);
CREATE INDEX idx_sensor_data_alert_level ON sensor_data(alert_level) WHERE alert_level != 'normal';

-- Partition by timestamp for better performance
CREATE TABLE sensor_data_2025_01 PARTITION OF sensor_data
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

-- ============================================
-- CAMERA & VISION
-- ============================================

CREATE TABLE camera_feeds (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    robot_id UUID REFERENCES robots(id) ON DELETE CASCADE,
    feed_url TEXT,
    resolution VARCHAR(20),
    fps INTEGER,
    is_active BOOLEAN DEFAULT true,
    stream_key VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE face_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    robot_id UUID REFERENCES robots(id) ON DELETE CASCADE,
    face_encoding BYTEA NOT NULL,
    image_path TEXT,
    confidence NUMERIC(5, 4),
    label VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_face_records_user_id ON face_records(user_id);
CREATE INDEX idx_face_records_robot_id ON face_records(robot_id);

CREATE TABLE detection_events (
    id BIGSERIAL PRIMARY KEY,
    robot_id UUID REFERENCES robots(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN 
        ('face_detected', 'motion_detected', 'human_detected', 'unknown_person', 'intrusion')),
    detected_object VARCHAR(100),
    confidence NUMERIC(5, 4),
    bounding_box JSONB,
    image_snapshot_path TEXT,
    video_clip_path TEXT,
    face_id UUID REFERENCES face_records(id) ON DELETE SET NULL,
    metadata JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_detection_events_robot_id ON detection_events(robot_id);
CREATE INDEX idx_detection_events_type ON detection_events(event_type);
CREATE INDEX idx_detection_events_timestamp ON detection_events(timestamp DESC);

-- ============================================
-- VOICE & CONVERSATION
-- ============================================

CREATE TABLE voice_logs (
    id BIGSERIAL PRIMARY KEY,
    robot_id UUID REFERENCES robots(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    audio_file_path TEXT,
    transcription TEXT,
    language VARCHAR(10) DEFAULT 'vi',
    confidence NUMERIC(5, 4),
    duration_seconds NUMERIC(6, 2),
    speaker_identity VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_voice_logs_robot_id ON voice_logs(robot_id);
CREATE INDEX idx_voice_logs_user_id ON voice_logs(user_id);
CREATE INDEX idx_voice_logs_timestamp ON voice_logs(timestamp DESC);

CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    robot_id UUID REFERENCES robots(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_id VARCHAR(100),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    total_messages INTEGER DEFAULT 0,
    sentiment_score NUMERIC(3, 2),
    summary TEXT
);

CREATE TABLE conversation_messages (
    id BIGSERIAL PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    message_type VARCHAR(20) CHECK (message_type IN ('user', 'robot', 'system')),
    content TEXT NOT NULL,
    intent VARCHAR(100),
    entities JSONB,
    emotion VARCHAR(50),
    voice_log_id BIGINT REFERENCES voice_logs(id) ON DELETE SET NULL,
    audio_response_path TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversation_messages_conversation_id ON conversation_messages(conversation_id);
CREATE INDEX idx_conversation_messages_timestamp ON conversation_messages(timestamp DESC);

-- ============================================
-- ROBOT BEHAVIOR & AI
-- ============================================

CREATE TABLE behavior_logs (
    id BIGSERIAL PRIMARY KEY,
    robot_id UUID REFERENCES robots(id) ON DELETE CASCADE,
    behavior_type VARCHAR(100) NOT NULL,
    behavior_name VARCHAR(255),
    trigger_event VARCHAR(100),
    trigger_data JSONB,
    action_taken TEXT,
    success BOOLEAN,
    error_message TEXT,
    duration_ms INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_behavior_logs_robot_id ON behavior_logs(robot_id);
CREATE INDEX idx_behavior_logs_type ON behavior_logs(behavior_type);
CREATE INDEX idx_behavior_logs_timestamp ON behavior_logs(timestamp DESC);

CREATE TABLE robot_emotions (
    id BIGSERIAL PRIMARY KEY,
    robot_id UUID REFERENCES robots(id) ON DELETE CASCADE,
    emotion VARCHAR(50) CHECK (emotion IN 
        ('happy', 'sad', 'excited', 'curious', 'alert', 'sleepy', 'neutral')),
    intensity NUMERIC(3, 2) CHECK (intensity >= 0 AND intensity <= 1),
    reason TEXT,
    display_animation VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_robot_emotions_robot_id ON robot_emotions(robot_id);
CREATE INDEX idx_robot_emotions_timestamp ON robot_emotions(timestamp DESC);

-- ============================================
-- ACTUATOR COMMANDS
-- ============================================

CREATE TABLE actuator_commands (
    id BIGSERIAL PRIMARY KEY,
    robot_id UUID REFERENCES robots(id) ON DELETE CASCADE,
    command_type VARCHAR(50) NOT NULL CHECK (command_type IN 
        ('move', 'speak', 'display', 'sound', 'light', 'servo', 'custom')),
    command VARCHAR(255) NOT NULL,
    parameters JSONB,
    source VARCHAR(50) CHECK (source IN ('user', 'ai', 'automation', 'schedule')),
    priority INTEGER DEFAULT 5 CHECK (priority >= 1 AND priority <= 10),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN 
        ('pending', 'sent', 'executing', 'completed', 'failed', 'cancelled')),
    sent_at TIMESTAMP WITH TIME ZONE,
    executed_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    response_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_actuator_commands_robot_id ON actuator_commands(robot_id);
CREATE INDEX idx_actuator_commands_status ON actuator_commands(status);
CREATE INDEX idx_actuator_commands_priority ON actuator_commands(priority);
CREATE INDEX idx_actuator_commands_created_at ON actuator_commands(created_at DESC);

-- ============================================
-- ALERTS & NOTIFICATIONS
-- ============================================

CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    robot_id UUID REFERENCES robots(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) CHECK (severity IN ('info', 'warning', 'danger', 'critical')),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    source_event_type VARCHAR(50),
    source_event_id BIGINT,
    metadata JSONB,
    is_read BOOLEAN DEFAULT false,
    is_resolved BOOLEAN DEFAULT false,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alerts_robot_id ON alerts(robot_id);
CREATE INDEX idx_alerts_user_id ON alerts(user_id);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_is_read ON alerts(is_read);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);

CREATE TABLE notification_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    channel VARCHAR(50) CHECK (channel IN ('email', 'push', 'sms', 'websocket')),
    alert_types JSONB DEFAULT '[]'::jsonb,
    min_severity VARCHAR(20) DEFAULT 'warning',
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, channel)
);

-- ============================================
-- SYSTEM SETTINGS & CONFIG
-- ============================================

CREATE TABLE robot_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    robot_id UUID REFERENCES robots(id) ON DELETE CASCADE UNIQUE,
    sensor_thresholds JSONB DEFAULT '{}'::jsonb,
    behavior_rules JSONB DEFAULT '{}'::jsonb,
    voice_settings JSONB DEFAULT '{}'::jsonb,
    camera_settings JSONB DEFAULT '{}'::jsonb,
    schedule JSONB DEFAULT '{}'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE system_logs (
    id BIGSERIAL PRIMARY KEY,
    level VARCHAR(20) CHECK (level IN ('debug', 'info', 'warning', 'error', 'critical')),
    service VARCHAR(100),
    message TEXT NOT NULL,
    stack_trace TEXT,
    metadata JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_service ON system_logs(service);
CREATE INDEX idx_system_logs_timestamp ON system_logs(timestamp DESC);

-- ============================================
-- WEBSOCKET CONNECTIONS
-- ============================================

CREATE TABLE websocket_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    connection_id VARCHAR(255) UNIQUE NOT NULL,
    connection_type VARCHAR(50) CHECK (connection_type IN ('esp32', 'laptop_ai', 'web_client', 'mobile')),
    robot_id UUID REFERENCES robots(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    ip_address INET,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT true,
    last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    connected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    disconnected_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_websocket_connections_type ON websocket_connections(connection_type);
CREATE INDEX idx_websocket_connections_robot_id ON websocket_connections(robot_id);
CREATE INDEX idx_websocket_connections_is_active ON websocket_connections(is_active);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Auto update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_robots_updated_at BEFORE UPDATE ON robots
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_face_records_updated_at BEFORE UPDATE ON face_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Auto increment conversation message count
CREATE OR REPLACE FUNCTION increment_conversation_messages()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversations 
    SET total_messages = total_messages + 1 
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER increment_messages AFTER INSERT ON conversation_messages
    FOR EACH ROW EXECUTE FUNCTION increment_conversation_messages();

-- ============================================
-- VIEWS
-- ============================================

-- Latest sensor readings per robot
CREATE VIEW latest_sensor_readings AS
SELECT DISTINCT ON (robot_id, sensor_type)
    robot_id,
    sensor_type,
    sensor_name,
    value,
    unit,
    alert_level,
    timestamp
FROM sensor_data
ORDER BY robot_id, sensor_type, timestamp DESC;

-- Robot health status
CREATE VIEW robot_health_status AS
SELECT 
    r.id,
    r.device_id,
    r.name,
    r.status,
    r.last_seen_at,
    COUNT(DISTINCT s.sensor_type) as active_sensors,
    COUNT(a.id) FILTER (WHERE a.severity IN ('danger', 'critical') AND NOT a.is_resolved) as critical_alerts
FROM robots r
LEFT JOIN sensor_data s ON r.id = s.robot_id AND s.timestamp > NOW() - INTERVAL '5 minutes'
LEFT JOIN alerts a ON r.id = a.robot_id
GROUP BY r.id, r.device_id, r.name, r.status, r.last_seen_at;

-- ============================================
-- INITIAL DATA
-- ============================================

-- Create default admin user (password: admin123 - CHANGE THIS!)
INSERT INTO users (email, username, password_hash, full_name, role, email_verified)
VALUES 
('admin@robothomeguard.com', 'admin', '$2b$10$rKvFJZXAYOZjKJP3nJxYdOnxJBqW5vHnJxqQVYwXZmFKLZE1zQj8m', 'System Administrator', 'admin', true);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO robot_web_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO robot_web_user;
GRANT USAGE ON SCHEMA public TO robot_web_user;