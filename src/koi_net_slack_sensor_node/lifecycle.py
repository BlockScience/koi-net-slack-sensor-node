import asyncio
from contextlib import asynccontextmanager
from koi_net.lifecycle import NodeLifecycle
from . import backfill


class SlackSensorLifecycle(NodeLifecycle):
    def set_slack_app(self, slack_app):
        self.slack_app = slack_app
    
    @asynccontextmanager
    async def async_run(self):
        print("called async run")
        try:
            self.start()
            asyncio.create_task(
                backfill.backfill_messages(self.slack_app, self.handler_context))
            yield
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()