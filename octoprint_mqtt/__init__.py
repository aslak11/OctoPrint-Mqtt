# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin
import paho.mqtt.client as mqtt
import json


class MqttPlugin(octoprint.plugin.SettingsPlugin, octoprint.plugin.AssetPlugin, octoprint.plugin.EventHandlerPlugin,
				 octoprint.plugin.TemplatePlugin):

	def get_template_configs(self):
		return [
			dict(type="settings", custom_bindings=False)
		]

	def get_settings_defaults(self):
		return dict(host="localhost", port=1883, topic="octoprint", username="", password="")

	def get_template_vars(self):
		return dict(host=self._settings.get(["host"]), port=self._settings.get(["port"]),
					topic=self._settings.get(["topic"]),
					username=self._settings.get(["username"]), password=self._settings.get(["password"]))

	Connected = False

	def on_connect(client, userdata, flags, rc):
		global Connected
		Connected = True

	def on_disconnect(client, rc, d, a):
		global Connected
		Connected = False

	def __init__(self):
		self.client = mqtt.Client()
		self.client.on_connect = self.on_connect
		self.client.on_disconnect = self.on_disconnect

	def on_event(self, event, payload):
		if event == "SettingsUpdated":
			self.client.disconnect()
			self.Connected = False
		self._logger.info(self.Connected)
		if not self.Connected:
			self.client.username_pw_set(self._settings.get(["username"]), self._settings.get(["password"]))
			self.client.connect(self._settings.get(["host"]), self._settings.get(["port"]))
			self.Connected = True
		# self._logger.info(self.client.publish("octoprint/" + event, json.dumps(payload)))
		response = self.client.publish(self._settings.get(["topic"]), json.dumps({"payload": payload, "event": event}))
		self._logger.info(response)
		if response[1] > 10 or response[0] != 0:
			self._logger.info("reconnecting")
			self.client = mqtt.Client()
			self.client.username_pw_set(self._settings.get(["username"]), self._settings.get(["password"]))
			self.client.connect(self._settings.get(["host"]), self._settings.get(["port"]))
			self.Connected = True

	def get_assets(self):
		# Define your plugin's asset files to automatically include in the
		# core UI here.
		return dict(
			js=["js/mqtt.js"],
			css=["css/mqtt.css"],
			less=["less/mqtt.less"]
		)

	##~~ Softwareupdate hook

	def get_update_information(self):
		# Define the configuration for your plugin to use with the Software Update
		# Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
		# for details.
		return dict(
			mqtt=dict(
				displayName="Mqtt Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="aslak11",
				repo="OctoPrint-Mqtt",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/aslak11/OctoPrint-Mqtt/archive/{target_version}.zip"
			)
		)


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Mqtt Plugin"

# Starting with OctoPrint 1.4.0 OctoPrint will also support to run under Python 3 in addition to the deprecated
# Python 2. New plugins should make sure to run under both versions for now. Uncomment one of the following
# compatibility flags according to what Python versions your plugin supports!
# __plugin_pythoncompat__ = ">=2.7,<3" # only python 2
__plugin_pythoncompat__ = ">=3,<4"  # only python 3


# __plugin_pythoncompat__ = ">=2.7,<4" # python 2 and 3

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = MqttPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}
