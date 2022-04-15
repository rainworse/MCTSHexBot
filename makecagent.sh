#!/bin/bash

g++ -c -fPIC agents/Group031/agent.cpp -o agents/Group031/agent.o
g++ -shared -Wl,-soname,cagent.so -o agents/Group031/cagent.so agents/Group031/agent.o
