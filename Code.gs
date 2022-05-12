//  EnrollmentFiles
//  -----------------------------------------------------------------------------------------------------
/*  Create list of all YYYY-MM-DD_enrollment_file sheets in current directory.
 */
class EnrollmentFiles
{
  constructor()
  {
    this.enrollment_files = [];

    const folder = DriveApp.getFileById(SpreadsheetApp.getActive().getId()).getParents().next();
    const all_spreadsheet_files = folder.getFilesByType('application/vnd.google-apps.spreadsheet');
    while (all_spreadsheet_files.hasNext())
    {
      let this_file = all_spreadsheet_files.next();
      if (/^\d{4}-\d{2}-\d{2}_enrollments$/.test(this_file.getName()))
      {
        this.enrollment_files.push(this_file);
      }
    }
  }
}

// textifySections()
// --------------------------------------------------------------------------------------------------------
/*  A user requested that the Section column is being treated as numbers even though not all section values
 *  are numeric. This nifty function forces the column to be text.
 *  This function runs each time the sheet is opened.
 */
function textifySections()
{
  const headers = SpreadsheetApp.getActive().getRange('a1:z1').getValues();
  let section_col = -1;
  for (let i=0; i<headers[0].length; i++)
  {
    if (headers[0][i] === 'Section')
    {
      section_col = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i];
      break;
    }
  }
  if (section_col === -1)
  {
    MailApp.sendEmail(
    {
      to: 'cvickery@qc.cuny.edu',
      name: 'QC Courses',
      subject: 'textifySections() did not textify Sections',
      body: 'Did not find the Sections column in order to make it Text instead of Auto.',
      htmlBody: '<p>Did not find the Sections column in order to make it Text instead of Auto.</p>',
    });
  }
  else
  {
     SpreadsheetApp.getActive().getRange(`${section_col}:${section_col}`).setNumberFormat('@');
  }
}

//  onOpen()
//  -------------------------------------------------------------------------------------------------------
function onOpen()
{
  // Create the menu
  const user_email = Session.getActiveUser().getEmail();
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Class Status Report')
    .addItem('Show report', 'showReport')
    .addItem('Email report to me', 'emailToUser')
    .addItem('Email report to opt-ins', 'emailReport')
    .addItem('Change num days', 'maxDays').addToUi();

  // Freeze header row of latest_enrollments, and boldface it
  const this_sheet = SpreadsheetApp.getActive();
  this_sheet.setFrozenRows(1);
  this_sheet.getRange('a1:z1').setFontWeight('bold');
  textifySections()

  // Set default number of days for the report.
  const props = PropertiesService.getDocumentProperties();
  props.setProperty('max_days', 7);
}


//  maxDays()
//  --------------------------------------------------------------------------------------------------------
/*  In case user doesn't want 1 week of data.
 */
function maxDays()
{
  const ui = SpreadsheetApp.getUi();
  const props = PropertiesService.getDocumentProperties();
  const max_days = parseInt(props.getProperty('max_days'));

  const prompt_str = `Enter maximum number of days for the report (currently ${max_days}):`;
  const response = ui.prompt(prompt_str, ui.ButtonSet.OK_CANCEL);
  if (response.getSelectedButton() === ui.Button.OK)
  {
    const response_text = response.getResponseText();
    const response_value = Math.max(2, parseInt(response_text));
    if (isNaN(response_value))
    {
      ui.alert(`"${response_text}" is not a number`);
    }
    else
    {
      props.setProperty('max_days', response_value);
      if (response_value != response_text) // string entered had stuff after the number
      {
        ui.alert(`New value set to ${response_value}. (You entered "${response_text}")`);
      }
    }
  }
}


// compare_file_names
// ---------------------------------------------------------------------------------------------------------
/* Given a pair of files, compare their names, making the newer one first.
 */
function compare_file_names(f1, f2)
{
  const n1 = f1.getName();
  const n2 = f2.getName();
  if (n1 < n2) return +1;
  if (n2 < n1) return -1;
  return 0;
}

//  generateReport()
//  --------------------------------------------------------------------------------------------------------
/*  Produce an html report showing course status changes over the past max_days days.
 */
function generateReport()
{
  const ef = new EnrollmentFiles();
  const props = PropertiesService.getDocumentProperties();
  const max_days = parseInt(props.getProperty('max_days'));
  const session_dates = SpreadsheetApp.openById('1YxcGZuGi5MS8SFSQ2iQ23SpNLVQKRlnvrF2onNkEPT8').getDataRange().getValues();
  const today = new Date();
  let session_is_ended = []; // Booleans indexed by term_code
  for (let row = 1; row < session_dates.length; row++)
  {
    session_is_ended[session_dates[row][0]] = new Date(session_dates[row][2]) < today;
  }

  // Sort the list of report sheets by file name
  const sorted = ef.enrollment_files.sort(compare_file_names);
  // Save just the latest ones
  while (sorted.length > max_days)
  {
    sorted.pop();
  }
  const latest_url = sorted[0].getUrl();
  const latest_file_name = sorted[0].getName();
  const latest_date = latest_file_name.substr(0, 10);
  props.setProperty('latest_date', latest_date);
  // Collect list of semester, course, class #, sections, seats, enrollment, and status for all courses, indexed by
  // semester:class_num, ordered by semester, course.
  let all_data = [];
  const codes_to_names = []; // Use semester codes for sorting, but use semester names for display
  for (file in sorted)
  {
    let enrollment_file = sorted[file];
    let file_date = enrollment_file.getName().substr(0,10);
    let values = SpreadsheetApp.open(enrollment_file).getSheetByName(enrollment_file.getName()+'.csv').getDataRange().getValues();
    let cols = [];
    for (let i = 0; i < values[0].length; i++)
    {
      cols[values[0][i].toLowerCase().replace(' ', '_').replace('#', 'num').replace('?', '')] = i;
    }
    let semester_code = cols['semester_code'];
    let semester_name = cols['semester_name'];
    let course = cols['course'];
    let class_num = cols['class_num'];
    let class_status = cols['class_status'];
    for (let row = 1; row < values.length; row++)
    {
      codes_to_names[values[row][semester_code]] = values[row][semester_name];
      let key = `${values[row][semester_code]}:${values[row][course]}:${values[row][class_num]}`;
      if (!all_data[key])
      {
        all_data[key] = [];
      }
      all_data[key].push(values[row][class_status]);
    }
  }

  // Build the list of new/changed classes first as a 2D array,
  //   then sort it by semester/course
  //   then filter out info for sessions that have ended
  //   then generate CSV to attach as a file, and as a HTML report for email body.
  let report_table = [];
  for (course in all_data)
  {
    let include_row = all_data[course].length < max_days // default: true for new classes; false otherwise
    let report_row = course.split(':');
    let row_status = '';
    for (let i = 0; i < all_data[course].length; i++)
    {
      if (row_status === '')
      {
        row_status = all_data[course][i];
      }
      let status = all_data[course][i];
      if (status !== row_status)
      {
        include_row = true;
      }
      report_row.push(status)
    }
    // Include class if it was added, cancelled or if the status changed
    if (include_row)
    {
      // Pad empty columns (newly-added classes)
      for (let i = all_data[course].length; i < max_days; i++)
      {
        report_row.push('--');
      }
      report_table.push(report_row);
    }
  }

  // Sort report_table by semester and course
  report_table.sort(function(a, b)
  {
    // [semester-code, course] : [semester-code, course]
    // Semester codes are numeric but courses are strings in the form 'discipline catalog_number'
    if (a[0] === b[0])
    {
      let course_1 = a[1].split(' ');
      let course_2 = b[1].split(' ');
      if (course_1[0] === course_2[0])
      {
        // Compare numeric part of catalog_numbers
        let n1 = parseFloat(course_1[1]);
        while (n1 > 1000) n1 /= 10;
        let n2 = parseFloat(course_2[1]);
        while (n2 > 1000) n2 /= 10;
        return n1 - n2;
      }
      else
      {
        // Compare discipline names
        if (course_1[0] > course_2[0]) return +1;
        return -1;
      }
    }
    // Compare numeric semester codes
    return a[0] - b[0];
  });

  // Generate the HTML report and the CSV file.
  let html_report = `<!DOCTYPE html>
  <html>
    <head>
      <style>
        body {
          font-family: sans-serif;
          }
        table {
          border-collapse: collapse;
        }
      td, th {
        border: 1px solid #ccc;
        padding: 0.5em;
      }
      th {
        background-color: #eee;
        border: 1px solid #666;
        }
      .new-semester {
        border-top: 2px solid black;
        }
      .cancelled {
        color:red;
      }
      </style>
    </head>
    <body>
      <p><em>A spreadsheet with current enrollment details for all sections of all QC classes is at
      <a href="${latest_url}">${latest_file_name}</a> on QC’s Google Drive.</em></p>
      <message>
      <table><tr><th>Semester</th><th>Course</th><th>Class Number</th>`;

  let csv_header_row = ['Semester', 'Course', 'Class Number'];
  for (file in sorted)
  {
    html_report += `<th>${sorted[file].getName().substr(0,10)}</th>`;
    csv_header_row.push(sorted[file].getName().substr(0,10));
  }
  html_report += '</tr>';
  let semester_name = '';
  let row_class = '';
  let csv_table = csv_header_row.join(',') + '\n';

  for (let row = 0; row < report_table.length; row++)
  {
    let cols = report_table[row];
    // Skip rows where the semester has ended
    if (session_is_ended[cols[0]])
    {
      continue;
    }
    cols[0] = codes_to_names[cols[0]];
    if (cols[0] !== semester_name)
    {
      semester_name = cols[0];
      row_class = 'new-semester';
    }
    else
    {
      row_class = '';
    }
    csv_table += cols.join(',') + '\n';
    html_report += `<tr>
        <td class="${row_class}">${cols[0]}</td>
        <td class="${row_class}">${cols[1]}</td>
        <td class="${row_class}">${cols[2]}</td>`;
    for (let col = 3; col < cols.length; col++)
    {
      let cell_class = '';
      if (cols[col] === "Cancelled")
      {
        cell_class = ' cancelled';
      }
      html_report += `<td class="${row_class}${cell_class}">${cols[col]}</td>`;
    }
    html_report += '</tr>';
  }
  html_report += '</table></body></html>';
  return {html: html_report, csv: csv_table};;
}


//  showReport()
//  ------------------------------------------------------------------------------------------------------------
/*  Generate and show the report interactively
 */
function showReport()
{
  const ui = SpreadsheetApp.getUi();
  // Get report body
  const report_obj = generateReport();
  const props = PropertiesService.getDocumentProperties();
  const latest_date = props.getProperty('latest_date');
  const today = new Date().toISOString().substr(0,10);
  let message = '';
  if (latest_date !== today)
  {
    message = '<p><span class="cancelled">No new data available from CUNYfirst today.</span> Repeating previous data.</p>';
  }
  const html = HtmlService.createHtmlOutput(report_obj.html.replace('<message>', message) +
      '<input type="button" value="Close" onclick="google.script.host.close()" />');
  ui.showModalDialog(html, `${latest_date} Class Status Report`);
}


//  emailReport()
//  ------------------------------------------------------------------------------------------------------------
/*  Generate and email a copy the report to opt-ins.
 */
function emailReport()
{
  // Side effect: Make sure the Sections column is Text rather than String as a way of cleaning up the daily
  // update process.
  textifySections();
  // Get report body
  const report_obj = generateReport();
  const props = PropertiesService.getDocumentProperties();
  const latest_date = props.getProperty('latest_date');
  const today_date = new Date().toISOString().substr(0,10);
  let message = `<p>The table below is also attached as <em>${latest_date} Class Status Report.csv</em>.</p>`;
  if (latest_date !== today_date)
  {
    message += '<p> <span class="cancelled">No new data available from CUNYfirst today.</span> Repeating previous data below.</p>';
  }

  // Recipient lists
  const opt_ins = SpreadsheetApp.openById('1O6qnOa1mwXEkhF1p1Q0Yj-fi490ExXqjjDVrkuCjVLQ').getDataRange().getValues();
  const transposed = opt_ins[0].map((col, i) => opt_ins.map(row => row[i]));
  const opt_in_to_list = transposed[0].slice(1, transposed[0].length);
  const opt_in_days_list = transposed[1].slice(1, transposed[0].length);
  const cc_list = transposed[2].slice(1, transposed[1].length).join(',');
  const bcc_list = transposed[3].slice(1, transposed[1].length).join(',');
  // For the Cc list, the Days column tells what days of the week to send a report to the email in the To column.
  // The days may be "All" for every day, "M-F" for Monday through Friday, or any mix of two+ letter day-abbreviations.
  // "Thinking refried beans are sumptuous", for example, would select Thursday, Friday, and Sunday.
  // So would "thsufr" or "Tues, Fri, and Sunday".
  const today_daynum = new Date().getDay();
  const today_day = ['Su','Mo','Tu', 'We', 'Th', 'Fr', 'Sa'][today_daynum];
  let to_list = [];
  for (let i = 0; i < opt_in_to_list.length; i++)
  {
    if ((/All/i.test(opt_in_days_list[i]) ||
         (/M-F/i.test(opt_in_days_list[i]) && (today_daynum > 0) && (today_daynum < 6)) ||
         RegExp(today_day, 'i').test(opt_in_days_list[i])))
    {
      to_list.push(opt_in_to_list[i]);
    }
  }

  try
  {
    MailApp.sendEmail(
    {
      to: to_list.join(','),
      name: 'QC Courses',
      cc: cc_list,
      bcc: bcc_list,
      subject: `${latest_date} Class Status Report`,
      body: 'The report was sent as a HTML table, and attached as a CSV file.',
      htmlBody: report_obj.html.replace('<message>', message),
      attachments: [Utilities.newBlob(report_obj.csv, 'text/csv', `${latest_date} Class Status Report.csv`)]
    });
  }
  catch (e)
  {
    MailApp.sendEmail(
    {
      to: to_list.join(','),
      name: 'QC Courses',
      cc: cc_list,
      bcc: bcc_list,
      subject: `${latest_date} Class Status Report`,
      body: `There was an error sending the report: ${e}. This email includes it only as an attachment.`,
      htmlBody: `<h1>${e}</h1><p>There was an error sending the report in the body of an email,
                 probably because it was too large (see error message above).
                 Here is the CSV file, as an  attachment.</p>`,
      attachments: [Utilities.newBlob(report_obj.csv, 'text/csv', `${latest_date} Class Status Report.csv`)]
    });
  }
}

//  emailToUser()
//  ------------------------------------------------------------------------------------------------------------
/*  Generate and email a copy of the report to the current user.
 */
function emailToUser()
{
  // Get report body
  const report_obj = generateReport();
  const props = PropertiesService.getDocumentProperties();
  const latest_date = props.getProperty('latest_date');
  const today = new Date().toISOString().substr(0,10);
  let message = `<p>The table below is also attached as <em>${latest_date} Class Status Report.csv</em>.</p>`;
  if (latest_date !== today)
  {
    message += '<p> <span class="cancelled">No new data available from CUNYfirst today.</span> Repeating previous data below.</p>';
  }

  // Recipient
  const user_email = Session.getActiveUser().getEmail();

  // If the sheet is too big, send it just as an attachment
  try
  {
    MailApp.sendEmail(
    {
      to: user_email,
      name: 'QC Courses',
      subject: `${latest_date} Class Status Report`,
      body: 'The report was sent as a HTML table, and attached as a CSV file.',
      htmlBody: report_obj.html.replace('<message>', message),
      attachments: [Utilities.newBlob(report_obj.csv, 'text/csv', `${latest_date} Class Status Report.csv`)]
    });
  }
  catch (e)
  {
    MailApp.sendEmail(
    {
      to: user_email,
      name: 'QC Courses',
      subject: `${latest_date} Class Status Report`,
      body: `There was an error sending the report: ${e}. This email includes it only as an attachment.`,
      htmlBody: `<h1>${e}</h1><p>There was an error sending the report in the body of an email,
                 probably because it was too large (see error message above). This happens when all the
                 courses for a new semester get loaded into CUNYfirst.
                 Here is the CSV file, as an  attachment.</p>`,
      attachments: [Utilities.newBlob(report_obj.csv, 'text/csv', `${latest_date} Class Status Report.csv`)]
    });
  }
}
