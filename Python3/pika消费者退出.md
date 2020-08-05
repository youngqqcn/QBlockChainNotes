pika消费者退出问题

> https://stackoverflow.com/questions/32220057/interrupt-thread-with-start-consuming-method-of-pika


```python
import threading
import pika

class WorkerThread(threading.Thread):
    def __init__(self):
        super(WorkerThread, self).__init__()
        self._is_interrupted = False

    def stop(self):
        self._is_interrupted = True

    def run(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters())
        channel = connection.channel()
        channel.queue_declare("queue")
        for message in channel.consume("queue", inactivity_timeout=1):
            if self._is_interrupted:
                break
            if not message:
                continue
            method, properties, body = message
            print(body)

def main():
    thread = WorkerThread()
    thread.start()
    # some main thread activity ...
    thread.stop()
    thread.join()

if __name__ == "__main__":
    main()
```