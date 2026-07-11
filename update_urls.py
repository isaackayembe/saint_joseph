#!/usr/bin/env python
# -*- coding: utf-8 -*-

with open('saint_joseph/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("login_url='saint_joseph:login'", "login_url='login'")
content = content.replace("redirect('saint_joseph:login')", "redirect('login')")

with open('saint_joseph/views.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Mise à jour terminée")
