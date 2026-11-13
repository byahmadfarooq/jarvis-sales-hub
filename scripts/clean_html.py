with open('D:/jarvis-sales-hub/frontend/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'id="chipContainer"' in l:
        lines[i+1] = '                            <button onclick="sendQuickPrompt(\'Draft a cold outreach campaign for Dental clinics in Columbus\')" class="chip-pill whitespace-nowrap"><i class="fa-solid fa-pen-nib text-blue-400 mr-1.5"></i>Draft Dental Campaign</button>\n'
        lines[i+2] = '                            <button onclick="sendQuickPrompt(\'What is our current lead pipeline diagnostic?\')" class="chip-pill whitespace-nowrap"><i class="fa-solid fa-chart-simple text-blue-400 mr-1.5"></i>Pipeline Diagnostic</button>\n'
        lines[i+3] = '                            <button onclick="sendQuickPrompt(\'Help me refine our value pitch to increase booking rate\')" class="chip-pill whitespace-nowrap"><i class="fa-solid fa-bullseye text-blue-400 mr-1.5"></i>Refine Value Pitch</button>\n'
        lines[i+4] = '                            <button onclick="sendQuickPrompt(\'Scan inbox for any new replies from prospects\')" class="chip-pill whitespace-nowrap"><i class="fa-solid fa-inbox text-blue-400 mr-1.5"></i>Scan Replies</button>\n'
        break

with open('D:/jarvis-sales-hub/frontend/index.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Cleaned chip icons successfully!')
