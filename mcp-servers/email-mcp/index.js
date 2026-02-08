const { Server, StdioTransport } = require('@modelcontextprotocol/sdk');
const nodemailer = require('nodemailer');
require('dotenv').config();

class EmailMCP {
  constructor() {
    this.transporter = null;
    this.initializeTransporter();
  }

  initializeTransporter() {
    // Using environment variables for security
    const smtpConfig = {
      host: process.env.SMTP_HOST || 'smtp.gmail.com',
      port: parseInt(process.env.SMTP_PORT) || 587,
      secure: false, // true for 465, false for other ports
      auth: {
        user: process.env.EMAIL_ADDRESS,
        pass: process.env.EMAIL_APP_PASSWORD, // Use app password for Gmail
      },
    };

    this.transporter = nodemailer.createTransporter(smtpConfig);

    // Verify the transporter configuration
    this.transporter.verify((error, success) => {
      if (error) {
        console.error('Email transporter configuration error:', error);
      } else {
        console.log('Email transporter is ready to send messages');
      }
    });
  }

  async sendEmail(recipient, subject, body, options = {}) {
    try {
      const mailOptions = {
        from: process.env.EMAIL_ADDRESS || '"AI Employee" <ai.employee@example.com>',
        to: recipient,
        cc: options.cc || undefined,
        bcc: options.bcc || undefined,
        subject: subject,
        text: options.textBody || body,
        html: options.htmlBody || `<p>${body.replace(/\n/g, '<br>')}</p>`,
        attachments: options.attachments || [],
      };

      const info = await this.transporter.sendMail(mailOptions);
      console.log('Email sent successfully:', info.messageId);
      return {
        success: true,
        messageId: info.messageId,
        recipient: recipient,
        subject: subject,
      };
    } catch (error) {
      console.error('Error sending email:', error);
      return {
        success: false,
        error: error.message,
        recipient: recipient,
        subject: subject,
      };
    }
  }

  async listEmails(query = '', maxResults = 10) {
    // This would integrate with Gmail API or other email providers
    // For now, returning a mock response
    return {
      success: true,
      count: 0,
      emails: [],
      query: query,
      maxResults: maxResults,
    };
  }

  async getUnreadEmails() {
    // This would integrate with Gmail API or other email providers
    // For now, returning a mock response
    return {
      success: true,
      count: 0,
      emails: [],
    };
  }
}

// MCP Server Implementation
async function createEmailMCPServer() {
  const server = new Server({
    name: 'email-mcp',
    version: '1.0.0',
  });

  const emailService = new EmailMCP();

  // Register capabilities
  server.capability('send-email', {
    description: 'Send an email to a recipient',
    inputSchema: {
      type: 'object',
      properties: {
        to: { type: 'string', description: 'Recipient email address' },
        subject: { type: 'string', description: 'Email subject' },
        body: { type: 'string', description: 'Email body content' },
        cc: { type: 'string', description: 'CC recipients (optional)' },
        bcc: { type: 'string', description: 'BCC recipients (optional)' },
        attachments: { 
          type: 'array', 
          items: { type: 'string' }, 
          description: 'File paths to attach (optional)' 
        },
      },
      required: ['to', 'subject', 'body'],
    },
    outputSchema: {
      type: 'object',
      properties: {
        success: { type: 'boolean' },
        messageId: { type: 'string' },
        error: { type: 'string' },
      },
    },
  });

  server.capability('list-emails', {
    description: 'List emails based on query',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Search query' },
        maxResults: { type: 'number', description: 'Maximum number of results' },
      },
      required: [],
    },
    outputSchema: {
      type: 'object',
      properties: {
        success: { type: 'boolean' },
        count: { type: 'number' },
        emails: { type: 'array' },
      },
    },
  });

  server.capability('get-unread-emails', {
    description: 'Get unread emails',
    inputSchema: {
      type: 'object',
      properties: {},
    },
    outputSchema: {
      type: 'object',
      properties: {
        success: { type: 'boolean' },
        count: { type: 'number' },
        emails: { type: 'array' },
      },
    },
  });

  // Handle capability calls
  server.handle('send-email', async ({ params }) => {
    return await emailService.sendEmail(
      params.to,
      params.subject,
      params.body,
      {
        cc: params.cc,
        bcc: params.bcc,
        attachments: params.attachments,
      }
    );
  });

  server.handle('list-emails', async ({ params }) => {
    return await emailService.listEmails(
      params.query || '',
      params.maxResults || 10
    );
  });

  server.handle('get-unread-emails', async () => {
    return await emailService.getUnreadEmails();
  });

  return server;
}

// Start the server
async function startServer() {
  try {
    const server = await createEmailMCPServer();
    const transport = new StdioTransport(server);
    await transport.listen();
    console.log('Email MCP Server listening via stdio');
  } catch (error) {
    console.error('Error starting Email MCP Server:', error);
    process.exit(1);
  }
}

if (require.main === module) {
  startServer();
}

module.exports = { EmailMCP, createEmailMCPServer };