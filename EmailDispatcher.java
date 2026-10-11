import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import javax.mail.*;
import javax.mail.internet.*;
import javax.activation.*;

public class EmailDispatcher {
    
    // ========== CONFIGURATION SETTINGS ==========
    private static final String SMTP_SERVER = "smtp.gmail.com";
    private static final int SMTP_PORT = 587;
    private static final String SENDER_EMAIL = "rajaluxanaa@gmail.com";  // CHANGE THIS
    private static final String SENDER_PASSWORD = "sjchxvbpbjihbdkx";  // CHANGE THIS
    
    private static final String SUBJECT = "Automated Email Dispatch";
    
    // Email settings
    private static final boolean USE_HTML = true;
    
    // Attachment settings (optional)
    private static final boolean SEND_ATTACHMENTS = false;  // Set to true to enable attachments
    private static final List<String> ATTACHMENT_FILES = Arrays.asList(
        // "report.pdf",    // Uncomment when needed
        // "invoice.pdf"    // Uncomment when needed
    );
    
    // Delay settings (seconds)
    private static final int MIN_DELAY = 3;
    private static final int MAX_DELAY = 7;
    
    // Department filter
    private static final String FILTER_DEPARTMENT = "All";  // Change to "Sales", "Support", etc.
    
    // Template settings
    private static final String TEMPLATE_FOLDER = "templates";
    private static final String TEMPLATE_NAME = "default";  // Change to "welcome", "newsletter", etc.
    
    // ============================================
    
    // Default HTML template
    private static final String DEFAULT_HTML_TEMPLATE = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #0066cc, #004499); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
                .content { background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }
                .footer { text-align: center; margin-top: 20px; font-size: 12px; color: #888; }
                .highlight { color: #0066cc; font-weight: bold; }
                .time { color: #28a745; font-size: 14px; }
                .department { background: #e7f3ff; padding: 10px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Automated Email Dispatch</h2>
                </div>
                <div class="content">
                    <h2>Hello <span class="highlight">{name}</span>!</h2>
                    <p>This is an <b>automated email</b> from your dispatch system.</p>
                    <div class="department">
                        <strong>Department:</strong> {department}
                    </div>
                    <p>Your automated report has been generated successfully.</p>
                    <p class="time"><strong>Sent at:</strong> {current_time}</p>
                    <hr>
                    <p>This is an automated message - no reply needed.</p>
                </div>
                <div class="footer">
                    <p>2025 Automated Email System</p>
                </div>
            </div>
        </body>
        </html>
        """;
    
    // Recipient class to store data
    static class Recipient {
        String name;
        String email;
        String department;
        
        Recipient(String name, String email, String department) {
            this.name = name;
            this.email = email;
            this.department = department;
        }
    }
    
    public static void main(String[] args) {
        System.out.println("\n" + "=".repeat(60));
        System.out.println("JAVA AUTOMATED EMAIL DISPATCHER");
        System.out.println("=".repeat(60));
        
        // Setup templates folder
        setupTemplatesFolder();
        
        // Show attachment status
        System.out.println("\n" + "=".repeat(50));
        System.out.println("ATTACHMENT STATUS");
        System.out.println("=".repeat(50));
        if (SEND_ATTACHMENTS) {
            System.out.println("Attachments: ENABLED");
            if (!ATTACHMENT_FILES.isEmpty()) {
                System.out.println("  Files to send: " + ATTACHMENT_FILES);
            }
        } else {
            System.out.println("Attachments: DISABLED");
        }
        System.out.println("=".repeat(50));
        
        // Ask for schedule
        Scanner scanner = new Scanner(System.in);
        System.out.print("\nDo you want to schedule this script? (y/n): ");
        String scheduleChoice = scanner.nextLine().toLowerCase();
        
        if (scheduleChoice.equals("y")) {
            System.out.print("Enter time (HH:MM, e.g., 09:00): ");
            String scheduleTime = scanner.nextLine();
            System.out.print("Enter day (monday/tuesday/etc.) or press Enter for daily: ");
            String scheduleDay = scanner.nextLine();
            
            System.out.println("\n[SCHEDULE] Scheduling is available in Java version with external libraries");
            System.out.println("[SCHEDULE] For now, running immediately...");
            sendBatchEmails();
        } else {
            sendBatchEmails();
        }
        
        scanner.close();
    }
    
    private static void setupTemplatesFolder() {
        File templateDir = new File(TEMPLATE_FOLDER);
        if (!templateDir.exists()) {
            templateDir.mkdir();
            System.out.println("[SETUP] Created '" + TEMPLATE_FOLDER + "' folder");
            
            // Create example templates
            String[] templateNames = {"default", "welcome", "newsletter", "invoice"};
            String[] templateContents = {
                DEFAULT_HTML_TEMPLATE,
                "<!DOCTYPE html>\n<html>\n<body>\n<h2>Welcome {name}!</h2>\n<p>Thank you for joining our {department} team.</p>\n<p>Sent at: {current_time}</p>\n</body>\n</html>",
                "<!DOCTYPE html>\n<html>\n<body>\n<h2>Monthly Newsletter - {current_time}</h2>\n<p>Hello {name},</p>\n<p>Updates from {department} department...</p>\n</body>\n</html>",
                "<!DOCTYPE html>\n<html>\n<body>\n<h2>Invoice for {name}</h2>\n<p>Department: {department}</p>\n<p>Please find your invoice attached.</p>\n</body>\n</html>"
            };
            
            for (int i = 0; i < templateNames.length; i++) {
                try {
                    FileWriter writer = new FileWriter(TEMPLATE_FOLDER + "/" + templateNames[i] + ".html");
                    writer.write(templateContents[i]);
                    writer.close();
                    System.out.println("[SETUP] Created template: " + TEMPLATE_FOLDER + "/" + templateNames[i] + ".html");
                } catch (IOException e) {
                    System.out.println("[SETUP] Error creating template: " + e.getMessage());
                }
            }
        }
    }
    
    private static String loadHtmlTemplate() {
        String templatePath = TEMPLATE_FOLDER + "/" + TEMPLATE_NAME + ".html";
        File templateFile = new File(templatePath);
        
        if (templateFile.exists()) {
            try {
                String content = new String(Files.readAllBytes(Paths.get(templatePath)));
                System.out.println("[TEMPLATE] Loaded: " + templatePath);
                return content;
            } catch (IOException e) {
                System.out.println("[TEMPLATE] Error loading template: " + e.getMessage());
                return DEFAULT_HTML_TEMPLATE;
            }
        } else {
            System.out.println("[TEMPLATE] Using default template");
            return DEFAULT_HTML_TEMPLATE;
        }
    }
    
    private static List<Recipient> readCsvFile() {
        List<Recipient> recipients = new ArrayList<>();
        String csvFile = "emails.csv";
        
        try (BufferedReader br = new BufferedReader(new FileReader(csvFile))) {
            String line = br.readLine(); // Skip header
            while ((line = br.readLine()) != null) {
                String[] data = line.split(",");
                if (data.length >= 3) {
                    recipients.add(new Recipient(data[0].trim(), data[1].trim(), data[2].trim()));
                }
            }
            System.out.println("[CSV] Loaded " + recipients.size() + " recipients");
        } catch (IOException e) {
            System.out.println("ERROR: emails.csv not found!");
            System.out.println("   Create emails.csv with columns: name,email,department");
            return new ArrayList<>();
        }
        
        return recipients;
    }
    
    private static List<Recipient> filterByDepartment(List<Recipient> recipients) {
        if (FILTER_DEPARTMENT.equals("All")) {
            return recipients;
        }
        
        List<Recipient> filtered = new ArrayList<>();
        for (Recipient r : recipients) {
            if (r.department.equals(FILTER_DEPARTMENT)) {
                filtered.add(r);
            }
        }
        
        System.out.println("\n[FILTER] Sending only to '" + FILTER_DEPARTMENT + "' department");
        System.out.println("[FILTER] Found " + filtered.size() + " recipients out of " + recipients.size());
        return filtered;
    }
    
    private static void logResult(String message) {
        String timestamp = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date());
        String logMessage = timestamp + " - " + message;
        System.out.println(logMessage);
        
        try (FileWriter fw = new FileWriter("log.txt", true);
             BufferedWriter bw = new BufferedWriter(fw);
             PrintWriter out = new PrintWriter(bw)) {
            out.println(logMessage);
        } catch (IOException e) {
            System.out.println("Error writing to log: " + e.getMessage());
        }
    }
    
    private static String personalizeTemplate(String template, String name, String department, String currentTime) {
        return template.replace("{name}", name)
                      .replace("{department}", department)
                      .replace("{current_time}", currentTime);
    }
    
    private static void sendEmail(Recipient recipient) {
        try {
            // Email properties
            Properties props = new Properties();
            props.put("mail.smtp.auth", "true");
            props.put("mail.smtp.starttls.enable", "true");
            props.put("mail.smtp.host", SMTP_SERVER);
            props.put("mail.smtp.port", SMTP_PORT);
            
            // Create session with authentication
            Session session = Session.getInstance(props, new Authenticator() {
                @Override
                protected PasswordAuthentication getPasswordAuthentication() {
                    return new PasswordAuthentication(SENDER_EMAIL, SENDER_PASSWORD);
                }
            });
            
            // Create email message
            MimeMessage message = new MimeMessage(session);
            message.setFrom(new InternetAddress(SENDER_EMAIL));
            message.setRecipient(Message.RecipientType.TO, new InternetAddress(recipient.email));
            message.setSubject(SUBJECT + " - " + recipient.name);
            
            // Get current time
            String currentTime = new java.text.SimpleDateFormat("hh:mm a 'on' MMMM dd, yyyy").format(new Date());
            
            // Load and personalize template
            String htmlTemplate = loadHtmlTemplate();
            String personalizedHtml = personalizeTemplate(htmlTemplate, recipient.name, recipient.department, currentTime);
            
            // Create multipart message for HTML + attachments
            MimeMultipart multipart = new MimeMultipart();
            
            // HTML body part
            MimeBodyPart htmlPart = new MimeBodyPart();
            htmlPart.setContent(personalizedHtml, "text/html; charset=utf-8");
            multipart.addBodyPart(htmlPart);
            
            // Add attachments if enabled
            if (SEND_ATTACHMENTS) {
                for (String filePath : ATTACHMENT_FILES) {
                    File file = new File(filePath);
                    if (file.exists()) {
                        MimeBodyPart attachmentPart = new MimeBodyPart();
                        attachmentPart.attachFile(file);
                        multipart.addBodyPart(attachmentPart);
                        System.out.println("   Attached: " + filePath);
                        logResult("[ATTACH] Attached file: " + filePath);
                    } else {
                        System.out.println("   WARNING: File not found: " + filePath);
                    }
                }
            }
            
            message.setContent(multipart);
            
            // Send email
            Transport.send(message);
            logResult("[SUCCESS] Sent to " + recipient.name + " (" + recipient.email + ") - Dept: " + recipient.department);
            
        } catch (MessagingException | IOException e) {
            logResult("[FAILED] " + recipient.name + " (" + recipient.email + ") - Error: " + e.getMessage());
        }
    }
    
    private static void sendBatchEmails() {
        System.out.println("\n" + "=".repeat(60));
        System.out.println("AUTOMATED EMAIL DISPATCHER (JAVA EDITION)");
        System.out.println("=".repeat(60));
        System.out.println("HTML Mode: " + (USE_HTML ? "ON" : "OFF"));
        System.out.println("Attachments: " + (SEND_ATTACHMENTS ? "ENABLED" : "DISABLED"));
        System.out.println("Template: " + TEMPLATE_NAME);
        System.out.println("Department Filter: " + FILTER_DEPARTMENT);
        System.out.println("Random Delay: " + MIN_DELAY + "-" + MAX_DELAY + " seconds");
        System.out.println("=".repeat(60) + "\n");
        
        // Read recipients from CSV
        List<Recipient> allRecipients = readCsvFile();
        if (allRecipients.isEmpty()) {
            System.out.println("ERROR: No recipients found!");
            return;
        }
        
        // Filter by department
        List<Recipient> recipients = filterByDepartment(allRecipients);
        if (recipients.isEmpty()) {
            System.out.println("WARNING: No recipients found for department '" + FILTER_DEPARTMENT + "'");
            return;
        }
        
        int successCount = 0;
        int total = recipients.size();
        Random random = new Random();
        
        for (int i = 0; i < total; i++) {
            Recipient r = recipients.get(i);
            System.out.println("\n[" + (i+1) + "/" + total + "] Sending to: " + r.name + " (" + r.department + ")");
            
            sendEmail(r);
            successCount++;
            
            // Random delay between emails
            if (i < total - 1) {
                int waitTime = random.nextInt(MAX_DELAY - MIN_DELAY + 1) + MIN_DELAY;
                System.out.println("   Waiting " + waitTime + " seconds before next email...");
                try {
                    TimeUnit.SECONDS.sleep(waitTime);
                } catch (InterruptedException e) {
                    System.out.println("   Delay interrupted");
                }
            }
        }
        
        // Summary
        System.out.println("\n" + "=".repeat(60));
        System.out.println("COMPLETE! Success: " + successCount + "/" + total + " emails sent");
        System.out.println("Failed: " + (total - successCount) + " emails");
        System.out.println("Detailed log saved to 'log.txt'");
        System.out.println("=".repeat(60));
    }
}