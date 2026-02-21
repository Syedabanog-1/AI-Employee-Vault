"""Generate the Complete Watcher Fix Guide as a PDF."""

from fpdf import FPDF


class GuidePDF(FPDF):
    def header(self):
        self.set_draw_color(0, 120, 200)
        self.set_line_width(0.5)
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(6)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'AI Employee - Watcher Authentication Fix Guide', align='C')
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', align='C')

    def section_title(self, title):
        self.ln(4)
        self.set_font('Helvetica', 'B', 16)
        self.set_text_color(0, 80, 160)
        self.cell(0, 10, title)
        self.ln(8)
        self.set_draw_color(0, 80, 160)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def sub_title(self, title):
        self.ln(2)
        self.set_font('Helvetica', 'B', 13)
        self.set_text_color(40, 40, 40)
        self.cell(0, 8, title)
        self.ln(8)

    def step_header(self, text):
        self.set_font('Helvetica', 'B', 11)
        self.set_text_color(0, 100, 50)
        self.cell(0, 7, text)
        self.ln(6)

    def body_text(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text):
        self.set_font('Helvetica', '', 10)
        self.set_text_color(30, 30, 30)
        self.cell(6, 5.5, '-')
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def code_block(self, text):
        self.set_fill_color(240, 240, 240)
        self.set_font('Courier', '', 9)
        self.set_text_color(30, 30, 30)
        x = self.get_x()
        w = self.w - 2 * self.l_margin
        lines = text.split('\n')
        block_h = len(lines) * 5.5 + 4
        if self.get_y() + block_h > self.h - 20:
            self.add_page()
        y_start = self.get_y()
        self.rect(x, y_start, w, block_h, 'F')
        self.ln(2)
        for line in lines:
            self.cell(4)
            self.cell(0, 5.5, line)
            self.ln(5.5)
        self.ln(4)

    def warning_box(self, text):
        self.set_fill_color(255, 245, 230)
        self.set_draw_color(255, 165, 0)
        self.set_line_width(0.4)
        x = self.get_x()
        w = self.w - 2 * self.l_margin
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(180, 100, 0)
        y_start = self.get_y()
        self.rect(x, y_start, w, 20, 'DF')
        self.ln(3)
        self.cell(4)
        self.multi_cell(w - 8, 5.5, text)
        self.ln(4)

    def info_box(self, text):
        self.set_fill_color(230, 243, 255)
        self.set_draw_color(0, 120, 200)
        self.set_line_width(0.4)
        x = self.get_x()
        w = self.w - 2 * self.l_margin
        lines = text.split('\n')
        block_h = len(lines) * 5.5 + 8
        if self.get_y() + block_h > self.h - 20:
            self.add_page()
        y_start = self.get_y()
        self.rect(x, y_start, w, block_h, 'DF')
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 60, 120)
        self.ln(3)
        for line in lines:
            self.cell(4)
            self.cell(0, 5.5, line)
            self.ln(5.5)
        self.ln(4)

    def table_row(self, cells, bold=False, fill=False):
        style = 'B' if bold else ''
        self.set_font('Helvetica', style, 9)
        if fill:
            self.set_fill_color(0, 80, 160)
            self.set_text_color(255, 255, 255)
        else:
            self.set_fill_color(248, 248, 248)
            self.set_text_color(30, 30, 30)
        col_widths = [45, 60, 85]
        for i, cell in enumerate(cells):
            self.cell(col_widths[i], 7, cell, border=1, fill=fill or (not bold and i % 2 == 0))
        self.ln()


def create_pdf():
    pdf = GuidePDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ===================== COVER / TITLE PAGE =====================
    pdf.add_page()
    pdf.ln(30)
    pdf.set_font('Helvetica', 'B', 28)
    pdf.set_text_color(0, 80, 160)
    pdf.cell(0, 15, 'Complete Fix Guide', align='C')
    pdf.ln(14)
    pdf.set_font('Helvetica', 'B', 22)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 12, 'All 3 Watchers Authentication', align='C')
    pdf.ln(12)

    pdf.set_draw_color(0, 120, 200)
    pdf.set_line_width(1)
    pdf.line(50, pdf.get_y(), 160, pdf.get_y())
    pdf.ln(12)

    pdf.set_font('Helvetica', '', 12)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 8, 'Gmail  |  WhatsApp  |  LinkedIn', align='C')
    pdf.ln(10)
    pdf.cell(0, 8, 'Personal AI Employee Hackathon 0 - Silver Tier', align='C')
    pdf.ln(20)

    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, 'AI Employee Vault Project', align='C')
    pdf.ln(6)
    pdf.cell(0, 8, 'February 2026', align='C')

    # ===================== ROOT CAUSE =====================
    pdf.add_page()
    pdf.section_title('Root Cause Analysis')

    pdf.body_text(
        'Your watchers cannot sign in because authentication was never set up. '
        'Each service (Gmail, WhatsApp, LinkedIn) requires a one-time OAuth/token '
        'setup before the watcher scripts can connect to their APIs.'
    )
    pdf.ln(2)

    pdf.sub_title('What Was Found')

    pdf.bullet('Gmail Watcher: The code tries to load gmail_token.json but this file was never created. '
               'The .env still has placeholder value: GOOGLE_REFRESH_TOKEN=your_google_refresh_token')
    pdf.bullet('WhatsApp Watcher: The file whatsapp_watcher.py did NOT EXIST in the watchers/ folder. '
               'Only an MCP server existed with simulated (fake) data.')
    pdf.bullet('LinkedIn Watcher: The file linkedin_watcher.py did NOT EXIST in the watchers/ folder. '
               'Only an MCP server existed with simulated (fake) data. '
               'The .env had placeholder values: LINKEDIN_CLIENT_ID=your_linkedin_client_id')

    pdf.ln(4)
    pdf.warning_box('SECURITY: Your .env contains real API keys. If this repo is public, rotate all keys immediately!')

    # ===================== GMAIL =====================
    pdf.add_page()
    pdf.section_title('WATCHER 1: Gmail - Fix Steps')

    pdf.sub_title('Problem')
    pdf.body_text(
        'No gmail_token.json exists. The Gmail watcher needs an OAuth2 token to authenticate '
        'with Google. The code calls Credentials.from_authorized_user_file() but the file '
        'was never created through the OAuth flow.'
    )

    pdf.step_header('Step 1: Install Required Packages')
    pdf.body_text('Open your terminal and run:')
    pdf.code_block('pip install google-auth google-auth-oauthlib google-api-python-client python-dotenv')

    pdf.step_header('Step 2: Set Up Google Cloud Project')
    pdf.body_text('Go to https://console.cloud.google.com/ and follow these sub-steps:')
    pdf.ln(1)
    pdf.bullet('Create a new project (or select an existing one)')
    pdf.bullet('Navigate to: APIs & Services > Library')
    pdf.bullet('Search for "Gmail API" and click Enable')
    pdf.bullet('Go to: APIs & Services > Credentials')
    pdf.bullet('Click "Create Credentials" > select "OAuth Client ID"')
    pdf.bullet('Application type: select "Desktop App"')
    pdf.bullet('Click "Create", then click "Download JSON"')
    pdf.bullet('Save the downloaded file as:')
    pdf.code_block(r'D:\Your_Name_Folder\AI_Employee_Vault_\credentials\client_secret.json')

    pdf.step_header('Step 3: Configure OAuth Consent Screen')
    pdf.body_text('Still in Google Cloud Console:')
    pdf.bullet('Go to "OAuth consent screen" in the left sidebar')
    pdf.bullet('User Type: Select "External" (or "Internal" if using Google Workspace)')
    pdf.bullet('Fill in the required fields (App name, user support email)')
    pdf.bullet('Under "Test users", click "Add Users"')
    pdf.bullet('Add YOUR Gmail address as a test user')
    pdf.bullet('Save and continue through all steps')

    pdf.step_header('Step 4: Run the Auth Setup (One Time Only)')
    pdf.body_text('This script opens your browser for Google sign-in and creates gmail_token.json:')
    pdf.code_block(
        r'cd "D:\Your_Name_Folder\AI_Employee_Vault_\credentials"' + '\n'
        r'python gmail_auth_setup.py'
    )
    pdf.ln(1)
    pdf.info_box(
        'What happens:\n'
        '1. A browser window opens automatically\n'
        '2. Sign in with your Google account\n'
        '3. Click "Allow" to grant Gmail read access\n'
        '4. gmail_token.json is created in the credentials/ folder\n'
        '5. You will see: "SETUP COMPLETE!" in the terminal'
    )

    pdf.step_header('Step 5: Run the Gmail Watcher')
    pdf.code_block(
        r'cd "D:\Your_Name_Folder\AI_Employee_Vault_\watchers"' + '\n'
        r'python gmail_watcher.py'
    )
    pdf.body_text('You should see: "Gmail API service initialized successfully!" -- This means it is working.')

    # ===================== WHATSAPP =====================
    pdf.add_page()
    pdf.section_title('WATCHER 2: WhatsApp - Fix Steps')

    pdf.sub_title('Problem')
    pdf.body_text(
        'There was NO whatsapp_watcher.py file in the watchers/ folder. A new one was '
        'created that uses the Meta WhatsApp Business Cloud API (the official way to '
        'programmatically access WhatsApp).'
    )

    pdf.step_header('Step 1: Create a Meta Developer App')
    pdf.body_text('Go to https://developers.facebook.com/ and:')
    pdf.bullet('Click "My Apps" in the top right, then "Create App"')
    pdf.bullet('Select app type: "Business"')
    pdf.bullet('Fill in app name (e.g., "AI Employee WhatsApp")')
    pdf.bullet('After the app is created, find "WhatsApp" in the products list')
    pdf.bullet('Click "Set Up" next to WhatsApp to add it to your app')

    pdf.step_header('Step 2: Get Your API Credentials')
    pdf.body_text('In your app dashboard, navigate to WhatsApp > API Setup:')
    pdf.ln(1)
    pdf.bullet('Temporary Access Token: You will see a token at the top. Click "Copy" to copy it. '
               'This is your WHATSAPP_ACCESS_TOKEN.')
    pdf.bullet('Phone Number ID: Shown below the token. This is your WHATSAPP_PHONE_NUMBER_ID.')
    pdf.bullet('WhatsApp Business Account ID: Shown in the sidebar or settings. '
               'This is your WHATSAPP_BUSINESS_ACCOUNT_ID.')

    pdf.step_header('Step 3: Update Your .env File')
    pdf.body_text('Open your .env file and replace the placeholder values with real ones:')
    pdf.code_block(
        'WHATSAPP_ACCESS_TOKEN=EAAGm0...your_real_token_here\n'
        'WHATSAPP_PHONE_NUMBER_ID=1234567890\n'
        'WHATSAPP_BUSINESS_ACCOUNT_ID=9876543210'
    )

    pdf.step_header('Step 4: Install Dependencies and Run')
    pdf.code_block(
        'pip install requests python-dotenv\n'
        r'cd "D:\Your_Name_Folder\AI_Employee_Vault_\watchers"' + '\n'
        'python whatsapp_watcher.py'
    )
    pdf.body_text('You should see: "WhatsApp credentials validated successfully!"')

    pdf.ln(2)
    pdf.warning_box('NOTE: Temporary access tokens expire in 24 hours. For production, submit app for review.')

    pdf.ln(4)
    pdf.set_draw_color(0, 80, 160)
    pdf.set_line_width(0.3)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(2)
    pdf.sub_title('Optional: Webhook Mode (Real-Time)')
    pdf.body_text(
        'For real-time message receiving (instead of polling), you can use webhook mode. '
        'This requires exposing a local server using ngrok:'
    )
    pdf.code_block(
        '# Install ngrok: https://ngrok.com/download\n'
        'ngrok http 8080\n'
        '\n'
        '# Set the ngrok URL as your webhook URL in Meta Developer Console:\n'
        '# WhatsApp > Configuration > Webhook URL: https://your-ngrok-url.ngrok.io\n'
        '# Verify Token: ai_employee_verify\n'
        '\n'
        '# Then run watcher in webhook mode:\n'
        'set WHATSAPP_WATCHER_MODE=webhook\n'
        'python whatsapp_watcher.py'
    )

    # ===================== LINKEDIN =====================
    pdf.add_page()
    pdf.section_title('WATCHER 3: LinkedIn - Fix Steps')

    pdf.sub_title('Problem')
    pdf.body_text(
        'There was NO linkedin_watcher.py file in the watchers/ folder. A new one was '
        'created that uses the LinkedIn API v2 with OAuth 2.0 authentication.'
    )

    pdf.step_header('Step 1: Create a LinkedIn Developer App')
    pdf.body_text('Go to https://www.linkedin.com/developers/ and:')
    pdf.bullet('Click "Create App"')
    pdf.bullet('Fill in: App name, LinkedIn Page (create one if needed), App logo')
    pdf.bullet('Accept the terms and click "Create App"')
    pdf.bullet('Under the "Products" tab, request access to:')
    pdf.body_text('    - "Sign In with LinkedIn using OpenID Connect"')
    pdf.body_text('    - "Share on LinkedIn" (for posting capabilities)')

    pdf.step_header('Step 2: Configure OAuth Settings')
    pdf.body_text('Under the "Auth" tab of your LinkedIn app:')
    pdf.bullet('Copy the "Client ID" value')
    pdf.bullet('Copy the "Client Secret" value (click the eye icon to reveal)')
    pdf.bullet('Under "OAuth 2.0 settings", click "Add redirect URL"')
    pdf.bullet('Add this exact URL: http://localhost:9090/callback')
    pdf.bullet('Click "Update" to save')

    pdf.step_header('Step 3: Update .env File')
    pdf.body_text('Add the Client ID and Secret to your .env:')
    pdf.code_block(
        'LINKEDIN_CLIENT_ID=86abc1234your_real_id\n'
        'LINKEDIN_CLIENT_SECRET=WPL...your_real_secret'
    )

    pdf.step_header('Step 4: Run LinkedIn Auth Setup (One Time)')
    pdf.code_block(
        'pip install requests python-dotenv\n'
        r'cd "D:\Your_Name_Folder\AI_Employee_Vault_\credentials"' + '\n'
        'python linkedin_auth_setup.py'
    )
    pdf.ln(1)
    pdf.info_box(
        'What happens:\n'
        '1. A browser window opens with LinkedIn login\n'
        '2. Sign in with your LinkedIn account\n'
        '3. Click "Allow" to grant permissions\n'
        '4. Browser shows "Success!"\n'
        '5. Terminal shows your access token\n'
        '6. Token is saved to credentials/linkedin_token.json'
    )

    pdf.step_header('Step 5: Copy Token to .env')
    pdf.body_text('The auth script prints your token. Copy it to .env:')
    pdf.code_block('LINKEDIN_ACCESS_TOKEN=AQV...the_long_token_from_step4')

    pdf.step_header('Step 6: Run the LinkedIn Watcher')
    pdf.code_block(
        r'cd "D:\Your_Name_Folder\AI_Employee_Vault_\watchers"' + '\n'
        'python linkedin_watcher.py'
    )
    pdf.body_text('You should see: "Authenticated as: Your Name" -- This means it is working.')

    pdf.ln(2)
    pdf.warning_box('NOTE: LinkedIn access tokens expire in 60 days. Re-run linkedin_auth_setup.py to renew.')

    # ===================== SUMMARY TABLE =====================
    pdf.add_page()
    pdf.section_title('Summary')

    pdf.sub_title('Problem & Fix Overview')
    # Table header
    pdf.table_row(['Watcher', 'Problem', 'Fix'], bold=True, fill=True)
    pdf.table_row(
        ['Gmail', 'No OAuth token file', 'Run gmail_auth_setup.py'],
    )
    pdf.table_row(
        ['WhatsApp', 'File did not exist + no token', 'Created watcher + get Meta token'],
    )
    pdf.table_row(
        ['LinkedIn', 'File did not exist + no token', 'Created watcher + run auth setup'],
    )

    pdf.ln(8)
    pdf.sub_title('Files Created / Fixed')

    pdf.set_font('Helvetica', 'B', 9)
    pdf.set_fill_color(0, 80, 160)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(110, 7, 'File Path', border=1, fill=True)
    pdf.cell(80, 7, 'Status', border=1, fill=True)
    pdf.ln()

    files = [
        ('credentials/gmail_auth_setup.py', 'NEW - One-time Gmail auth'),
        ('credentials/linkedin_auth_setup.py', 'NEW - One-time LinkedIn auth'),
        ('watchers/gmail_watcher.py', 'FIXED - Proper token + auto-refresh'),
        ('watchers/whatsapp_watcher.py', 'NEW - Meta Cloud API watcher'),
        ('watchers/linkedin_watcher.py', 'NEW - LinkedIn API v2 watcher'),
    ]

    for filepath, status in files:
        pdf.set_font('Courier', '', 8)
        pdf.set_text_color(30, 30, 30)
        pdf.set_fill_color(248, 248, 248)
        pdf.cell(110, 7, filepath, border=1, fill=True)
        pdf.set_font('Helvetica', 'B', 9)
        if 'NEW' in status:
            pdf.set_text_color(0, 130, 0)
        else:
            pdf.set_text_color(0, 80, 160)
        pdf.cell(80, 7, status, border=1)
        pdf.ln()

    pdf.ln(8)
    pdf.sub_title('Recommended Order')
    pdf.body_text('Start with the easiest and work your way up:')
    pdf.ln(2)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(0, 130, 0)
    pdf.cell(8, 7, '1.')
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 7, 'Gmail (easiest - just Google Cloud Console + run auth script)')
    pdf.ln(8)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(255, 165, 0)
    pdf.cell(8, 7, '2.')
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 7, 'LinkedIn (medium - create developer app + OAuth flow)')
    pdf.ln(8)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.set_text_color(200, 0, 0)
    pdf.cell(8, 7, '3.')
    pdf.set_font('Helvetica', '', 11)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 7, 'WhatsApp (hardest - Meta Business verification + webhook setup)')
    pdf.ln(10)

    pdf.set_draw_color(0, 120, 200)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)

    pdf.set_font('Helvetica', 'I', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 8, 'Generated for AI Employee Hackathon 0 - Silver Tier', align='C')
    pdf.ln(6)
    pdf.cell(0, 8, 'If you get stuck on any step, ask for help!', align='C')

    # Save
    output_path = r'D:\syeda Gulzar Bano\AI_Employee_Vault_\Watcher_Auth_Fix_Guide.pdf'
    pdf.output(output_path)
    print(f"PDF saved to: {output_path}")
    return output_path


if __name__ == '__main__':
    create_pdf()
