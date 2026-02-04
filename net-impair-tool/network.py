"""
Network packet manipulation module using pydivert/WinDivert
Provides lag, drop, throttle, duplicate, out-of-order, and tamper effects
"""

import pydivert
import threading
import time
import random
import struct
from collections import deque
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PacketEffect(Enum):
    """ประเภทของ effect ที่ apply ให้ packets"""
    LAG = "lag"
    DROP = "drop"
    THROTTLE = "throttle"
    DUPLICATE = "duplicate"
    OUT_OF_ORDER = "out_of_order"
    TAMPER = "tamper"


@dataclass
class NetworkConfig:
    """Configuration สำหรับ network impairment"""
    enabled: bool = False
    filter_str: str = "outbound and udp"
    
    # Lag settings
    lag_enabled: bool = False
    lag_ms: int = 100
    
    # Drop settings
    drop_enabled: bool = False
    drop_chance: float = 5.0  # percentage
    
    # Throttle settings
    throttle_enabled: bool = False
    throttle_ms: int = 10
    throttle_chance: float = 50.0  # percentage
    
    # Duplicate settings
    duplicate_enabled: bool = False
    duplicate_count: int = 1
    duplicate_chance: float = 10.0  # percentage
    
    # Out-of-order settings
    out_of_order_enabled: bool = False
    out_of_order_chance: float = 20.0  # percentage
    ooo_queue_size: int = 5
    
    # Tamper settings
    tamper_enabled: bool = False
    tamper_chance: float = 5.0  # percentage


class PacketQueue:
    """Queue สำหรับ packets ที่ต้อง delay / reorder"""
    def __init__(self, max_size: int = 100):
        self.queue = deque(maxlen=max_size)
        self.lock = threading.Lock()
        self.stats = {
            'processed': 0,
            'dropped': 0,
            'delayed': 0,
            'duplicated': 0,
            'tampered': 0,
            'out_of_order': 0
        }
    
    def add(self, packet: Any, delay_ms: float = 0, timestamp: Optional[float] = None):
        """เพิ่ม packet ลงใน queue พร้อม timestamp"""
        if timestamp is None:
            timestamp = time.time()
        
        with self.lock:
            self.queue.append({
                'packet': packet,
                'timestamp': timestamp,
                'delay': delay_ms,
                'ready_time': timestamp + (delay_ms / 1000.0)
            })
    
    def get_ready_packets(self):
        """ได้ packets ที่ ready ส่ง (delay time expired)"""
        current_time = time.time()
        ready = []
        
        with self.lock:
            while self.queue and self.queue[0]['ready_time'] <= current_time:
                ready.append(self.queue.popleft())
        
        return ready
    
    def get_stats(self):
        """ได้ statistics"""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset statistics"""
        with self.lock:
            for key in self.stats:
                self.stats[key] = 0


class NetworkImpairmentEngine:
    """หลักของ packet manipulation engine"""
    
    def __init__(self):
        self.config = NetworkConfig()
        self.packet_queue = PacketQueue()
        self.is_running = False
        self.capture_thread = None
        self.process_thread = None
        self.divert_handle = None
        self.lock = threading.Lock()
        self.ooo_buffer = deque(maxlen=10)  # สำหรับ out-of-order
    
    def start(self):
        """เริ่ม capture และ process packets"""
        if self.is_running:
            logger.warning("Network engine is already running")
            return False
        
        try:
            self.is_running = True
            
            # Create WinDivert handle กับ filter string
            logger.info(f"Opening WinDivert with filter: {self.config.filter_str}")
            self.divert_handle = pydivert.WinDivert(self.config.filter_str)
            self.divert_handle.open()
            
            # Start capture thread
            self.capture_thread = threading.Thread(
                target=self._capture_loop,
                daemon=True,
                name="PacketCapture"
            )
            self.capture_thread.start()
            
            # Start process thread (สำหรับ delayed packets)
            self.process_thread = threading.Thread(
                target=self._process_loop,
                daemon=True,
                name="PacketProcess"
            )
            self.process_thread.start()
            
            logger.info("Network impairment engine started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start engine: {e}")
            self.is_running = False
            return False
    
    def stop(self):
        """หยุด capture และ process"""
        if not self.is_running:
            return True
        
        self.is_running = False
        
        # Close WinDivert handle
        if self.divert_handle:
            try:
                self.divert_handle.close()
            except Exception as e:
                logger.error(f"Error closing divert handle: {e}")
            self.divert_handle = None
        
        # Wait for threads
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        if self.process_thread:
            self.process_thread.join(timeout=2)
        
        logger.info("Network impairment engine stopped")
        return True
    
    def _capture_loop(self):
        """Main loop สำหรับ capture packets"""
        logger.info("Packet capture loop started")
        
        try:
            while self.is_running and self.divert_handle:
                try:
                    # Receive packet
                    packets = self.divert_handle.recv(timeout=100)
                    
                    if not packets:
                        continue
                    
                    for packet in packets:
                        # Apply effects ตาม config
                        self._apply_effects(packet)
                        
                        self.packet_queue.stats['processed'] += 1
                
                except Exception as e:
                    if self.is_running:
                        logger.debug(f"Recv error: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Capture loop error: {e}")
        finally:
            logger.info("Packet capture loop ended")
    
    def _process_loop(self):
        """Loop สำหรับ process delayed packets"""
        logger.info("Packet process loop started")
        
        try:
            while self.is_running:
                # ได้ packets ที่ ready
                ready_packets = self.packet_queue.get_ready_packets()
                
                # ส่ง packets
                for item in ready_packets:
                    try:
                        if self.divert_handle:
                            self.divert_handle.send(item['packet'])
                    except Exception as e:
                        logger.debug(f"Send error: {e}")
                
                time.sleep(0.001)  # 1ms loop
        
        except Exception as e:
            logger.error(f"Process loop error: {e}")
        finally:
            logger.info("Packet process loop ended")
    
    def _apply_effects(self, packet):
        """Apply effects ให้กับ packet ตาม config"""
        
        # Drop check
        if self.config.drop_enabled:
            if random.random() * 100 < self.config.drop_chance:
                self.packet_queue.stats['dropped'] += 1
                return  # drop packet นี้
        
        # Duplicate check (ทำก่อน lag เพื่อให้ duplicate ได้ lag ด้วย)
        duplicate_count = 0
        if self.config.duplicate_enabled:
            if random.random() * 100 < self.config.duplicate_chance:
                duplicate_count = self.config.duplicate_count
                self.packet_queue.stats['duplicated'] += duplicate_count
        
        # Tamper check
        if self.config.tamper_enabled:
            if random.random() * 100 < self.config.tamper_chance:
                self._tamper_packet(packet)
                self.packet_queue.stats['tampered'] += 1
        
        # Out-of-order check (ใช้ simple random delay within range)
        delay = 0
        if self.config.out_of_order_enabled:
            if random.random() * 100 < self.config.out_of_order_chance:
                # Random delay 0-100ms เพื่อ reorder
                delay = random.random() * 100
                self.packet_queue.stats['out_of_order'] += 1
        
        # Throttle check
        if self.config.throttle_enabled:
            if random.random() * 100 < self.config.throttle_chance:
                delay += random.random() * self.config.throttle_ms
        
        # Lag
        if self.config.lag_enabled:
            delay += self.config.lag_ms
            self.packet_queue.stats['delayed'] += 1
        
        # Add to queue (พร้อม delay)
        self.packet_queue.add(packet, delay)
        
        # Add duplicates
        for _ in range(duplicate_count):
            # Deep copy packet สำหรับ duplicate
            try:
                dup_packet = packet.copy()
                self.packet_queue.add(dup_packet, delay)
            except Exception as e:
                logger.debug(f"Duplicate copy error: {e}")
    
    def _tamper_packet(self, packet):
        """แก้ไข packet payload เล็กน้อย"""
        try:
            if hasattr(packet, 'payload') and packet.payload:
                # Flip bit ใน payload ถ้า payload มี
                payload = bytearray(packet.payload)
                if len(payload) > 0:
                    # Flip bit แรก
                    idx = random.randint(0, len(payload) - 1)
                    payload[idx] ^= 0x01
                    packet.payload = bytes(payload)
                    
                    # Recalculate checksums
                    try:
                        packet.calc_checksums()
                    except Exception as e:
                        logger.debug(f"Checksum error: {e}")
        except Exception as e:
            logger.debug(f"Tamper error: {e}")
    
    def update_config(self, config_dict: Dict[str, Any]):
        """Update configuration"""
        with self.lock:
            for key, value in config_dict.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            logger.info(f"Config updated: {config_dict}")
    
    def get_stats(self):
        """ได้ statistics ปัจจุบัน"""
        stats = self.packet_queue.get_stats()
        stats['running'] = self.is_running
        stats['queue_size'] = len(self.packet_queue.queue)
        return stats
    
    def get_config(self):
        """ได้ config ปัจจุบัน"""
        return {
            'enabled': self.config.enabled,
            'filter_str': self.config.filter_str,
            'lag_enabled': self.config.lag_enabled,
            'lag_ms': self.config.lag_ms,
            'drop_enabled': self.config.drop_enabled,
            'drop_chance': self.config.drop_chance,
            'throttle_enabled': self.config.throttle_enabled,
            'throttle_ms': self.config.throttle_ms,
            'throttle_chance': self.config.throttle_chance,
            'duplicate_enabled': self.config.duplicate_enabled,
            'duplicate_count': self.config.duplicate_count,
            'duplicate_chance': self.config.duplicate_chance,
            'out_of_order_enabled': self.config.out_of_order_enabled,
            'out_of_order_chance': self.config.out_of_order_chance,
            'ooo_queue_size': self.config.ooo_queue_size,
            'tamper_enabled': self.config.tamper_enabled,
            'tamper_chance': self.config.tamper_chance,
        }


# Global engine instance
engine = NetworkImpairmentEngine()
