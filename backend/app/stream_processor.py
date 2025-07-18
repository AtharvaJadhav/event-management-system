import asyncio
import random
import logging
from pathlib import Path
from typing import Optional

from app.services import event_service

SAMPLE_FILE = Path(__file__).parent.parent / "data" / "sample_events.txt"

class AsyncStreamProcessor:
    def __init__(self):
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self.events_processed = 0
        self.last_result = None

    async def _process_stream(self):
        logging.info("Stream processor started.")
        self.events_processed = 0
        try:
            with SAMPLE_FILE.open("r") as f:
                for line in f:
                    if not self._running:
                        break
                    event_text = line.strip()
                    if not event_text:
                        continue
                    delay = random.uniform(2, 10)
                    await asyncio.sleep(delay)
                    try:
                        # Run the synchronous parse_event_text in a thread pool
                        loop = asyncio.get_event_loop()
                        parsed_events = await loop.run_in_executor(None, event_service.parse_event_text, event_text)
                        logging.info(f"Processed: {event_text} => {len(parsed_events)} events")
                        
                        # Try to create the events in the system
                        created_events = []
                        for event in parsed_events:
                            try:
                                # Convert Event to EventCreate and save
                                from app.models import EventCreate
                                event_create = EventCreate(**event.dict())
                                created_event = event_service.create_event(event_create)
                                created_events.append(created_event)
                                logging.info(f"Created event: {created_event.title}")
                            except Exception as create_error:
                                logging.warning(f"Failed to create event '{event.title}': {create_error}")
                        
                        self.last_result = {
                            "text": event_text, 
                            "result": [event.dict() for event in parsed_events],
                            "created": [event.dict() for event in created_events]
                        }
                    except Exception as e:
                        logging.error(f"Failed to process '{event_text}': {e}")
                        self.last_result = {"text": event_text, "error": str(e)}
                    self.events_processed += 1
        finally:
            self._running = False
            logging.info("Stream processor stopped.")

    def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._process_stream())

    def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()

    def status(self):
        return {
            "running": self._running,
            "events_processed": self.events_processed,
            "last_result": self.last_result,
        } 