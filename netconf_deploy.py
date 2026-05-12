<?xml version="1.0" encoding="UTF-8"?>
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">

    <hostname>CSR1kv-Task36</hostname>

    <interface>
      <GigabitEthernet>
        <name>1</name>
        <description>LAN - Task36</description>
        <ip>
          <address>
            <primary>
              <address>192.168.100.20</address>
              <mask>255.255.255.0</mask>
            </primary>
          </address>
        </ip>
      </GigabitEthernet>

      <GigabitEthernet>
        <name>2</name>
        <description>WAN - Task36</description>
        <ip>
          <address>
            <primary>
              <address>10.0.0.1</address>
              <mask>255.255.255.0</mask>
            </primary>
          </address>
        </ip>
      </GigabitEthernet>
    </interface>

    <router>
      <ospf xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-ospf">
        <id>1</id>
        <router-id>1.1.1.1</router-id>
        <network>
          <ip>192.168.100.0</ip>
          <mask>0.0.0.255</mask>
          <area>0</area>
        </network>
        <network>
          <ip>10.0.0.0</ip>
          <mask>0.0.0.255</mask>
          <area>0</area>
        </network>
      </ospf>
    </router>

  </native>
</config>
