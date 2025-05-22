from random import randint, uniform
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from random import randint
import os
from PIL import Image
from reportlab.lib.utils import ImageReader

def export_to_pdf(data):
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4

    c = canvas.Canvas("marschzeit-grid.pdf", pagesize=A4)
    w, h = A4
    max_rows_per_page = 45

    # Layout settings
    x_offset = 20
    y_offset = 200
    row_height = 16
    third_table_height = row_height * 7  # Height of the third table

    # Table column widths
    col_widths = [130, 20, 30, 30, 30, 30, 30, 30, 30, 35, 35, 30]

    # Compute x positions for main table
    xlist = [x_offset]
    for width in col_widths:
        xlist.append(xlist[-1] + width)

    # Y positions for main table (normal row heights)
    ylist = [h - y_offset - i * row_height for i in range(max_rows_per_page + 1)]

    # Y positions for second table (first row taller)
    ylist_second = [h - y_offset+row_height*7] # move table up the first cell
    for i in range(1, max_rows_per_page + 1):
        if i == 1:
            ylist_second.append(ylist_second[-1] - row_height * 8)  # First row big
        else:
            ylist_second.append(ylist_second[-1] - row_height)       # Normal rows

    # Where to start second column (right of the main table)
    second_grid_x_start = xlist[-1] + 0  # leave a gap between tables
    second_grid_width = 100
    second_grid_xlist = [second_grid_x_start, second_grid_x_start + second_grid_width]

    text_columns_left_aligned = [0, 12]  # "Ort" and "Bemerkung"

    third_table_y_top = ylist[0] + third_table_height

    for rows in grouper(data, max_rows_per_page):
        rows = tuple(filter(bool, rows))


        # --- sixth table ---
        top_table_col_widths = [60, 120]  # adjustable
        top_table_x = [20]  # start at the left side
        for width in top_table_col_widths:
            top_table_x.append(top_table_x[-1] + width)

        # Increase the height to allow multiple lines
        top_table_row_height = row_height * 4  # taller row
        top_table_y_top = ylist[0] + third_table_height + row_height # move up more
        top_table_y_bottom = top_table_y_top - top_table_row_height

        # Horizontal lines
        c.line(top_table_x[0], top_table_y_top, top_table_x[-1], top_table_y_top)
        c.line(top_table_x[0], top_table_y_bottom, top_table_x[-1], top_table_y_bottom)

        # Vertical lines
        for x in top_table_x:
            c.line(x, top_table_y_top, x, top_table_y_bottom)

        # Draw text in cells (centered)
        top_table_values = ["erstellt von:", "Alex\nIgnazio"]
        for i, text in enumerate(top_table_values):
            lines = text.split("\n")
            x_left = top_table_x[i]
            x_right = top_table_x[i + 1]
            cell_center_x = (x_left + x_right) / 2

            c.setFont("Helvetica", 9)
            total_text_height = len(lines) * 10  # approx line height = 10
            start_y = top_table_y_bottom + (top_table_row_height + total_text_height) / 2 - 10

            for j, line in enumerate(lines):
                text_width = c.stringWidth(line, "Helvetica", 9)
                c.drawString(cell_center_x - text_width / 2, start_y - j * 10, line)

    
        # --- seventh table (1 column, 2 rows, same position as sixth) ---
        seventh_table_col_width = 180  # adjustable width
        seventh_table_x = [20, 20 + seventh_table_col_width]

        # Adjust the height: first row = 1x, second row = 3x
        seventh_table_row_heights = [row_height, row_height * 3]
        seventh_table_y_top = top_table_y_top - row_height * 4  # align vertically as needed

        # Calculate y positions from top to bottom
        seventh_table_y = [seventh_table_y_top]
        for rh in seventh_table_row_heights:
            seventh_table_y.append(seventh_table_y[-1] - rh)

        # Horizontal lines
        c.line(seventh_table_x[0], seventh_table_y[0], seventh_table_x[-1], seventh_table_y[0])
        c.line(seventh_table_x[0], seventh_table_y[-1], seventh_table_x[-1], seventh_table_y[-1])
        c.line(seventh_table_x[0], seventh_table_y[1], seventh_table_x[-1], seventh_table_y[1])

        # Vertical lines
        for x in seventh_table_x:
            c.line(x, seventh_table_y[0], x, seventh_table_y[-1])

        # Optional: Example content (adjust as needed)
        seventh_table_values = ["Landeskarten:", "Alexs Landeskarte (jetzt mit mehr Eiern)"]
        for row_index, text in enumerate(seventh_table_values):
            c.setFont("Helvetica", 9)
            text_width = c.stringWidth(text, "Helvetica", 9)
            
            # Horizontal center between the two vertical lines
            cell_center_x = (seventh_table_x[0] + seventh_table_x[1]) / 2

            # Get current row height (first is row_height, second is row_height * 3)
            row_height_current = seventh_table_row_heights[row_index]

            # Calculate vertical center of the row
            row_top = seventh_table_y[row_index]
            row_bottom = seventh_table_y[row_index + 1]
            text_y = row_bottom + (row_height_current - 9) / 2  # 9 is font size

            # Draw centered text
            c.drawString(cell_center_x - text_width / 2, text_y, text)


        # --- fifth table ---
        top_table_col_widths = [60, 400, 100]  # adjustable
        top_table_x = [20]  # start at the left side
        for width in top_table_col_widths:
            top_table_x.append(top_table_x[-1] + width)

        top_table_y_top = ylist[0] + third_table_height + row_height*2  # adjust to be above the other two tables
        top_table_y_bottom = top_table_y_top - row_height

        # Horizontal lines
        c.line(top_table_x[0], top_table_y_top, top_table_x[-1], top_table_y_top)
        c.line(top_table_x[0], top_table_y_bottom, top_table_x[-1], top_table_y_bottom)

        # Vertical lines
        for x in top_table_x:
            c.line(x, top_table_y_top, x, top_table_y_bottom)

        # Draw text in cells
        top_table_values = ["Route:", "Crazy Routenname: HIER KÖNNTE IHRE WERBUNG STEHEN", "Geschwindigkeitsfaktor:"]
        for i, text in enumerate(top_table_values):
            x = top_table_x[i]
            c.setFont("Helvetica", 9)
            text_width = c.stringWidth(text, "Helvetica", 9)
            cell_center = (top_table_x[i] + top_table_x[i + 1]) / 2
            c.drawString(cell_center - text_width / 2, top_table_y_bottom + 4, text)

        # --- fouth table ---
        top_table_col_widths = [120, 160, 100]  # adjustable
        top_table_x = [200]  # start at the end of the main table
        for width in top_table_col_widths:
            top_table_x.append(top_table_x[-1] + width)

        top_table_y_top = ylist[0] + third_table_height + row_height  # adjust to be above the other two tables
        top_table_y_bottom = top_table_y_top - row_height

        # Horizontal lines
        c.line(top_table_x[0], top_table_y_top, top_table_x[-1], top_table_y_top)
        c.line(top_table_x[0], top_table_y_bottom, top_table_x[-1], top_table_y_bottom)

        # Vertical lines
        for x in top_table_x:
            c.line(x, top_table_y_top, x, top_table_y_bottom)

        # Draw text in cells
        top_table_values = ["Zwischenwerte", "Gesamtsummen", "4.5 (Lkm/h)"]
        for i, text in enumerate(top_table_values):
            x = top_table_x[i]
            c.setFont("Helvetica", 9)
            text_width = c.stringWidth(text, "Helvetica", 9)
            cell_center = (top_table_x[i] + top_table_x[i + 1]) / 2
            c.drawString(cell_center - text_width / 2, top_table_y_bottom + 4, text)

        # --- Draw Third Table (above "hm" to "Pause") ---
        start_col = 3  # "hm" column index
        end_col = len(col_widths)  # up to "Pause"
        third_table_x = xlist[start_col:end_col + 1]

        # Horizontal lines
        c.line(third_table_x[0], third_table_y_top, third_table_x[-1], third_table_y_top)
        c.line(third_table_x[0], third_table_y_top - third_table_height, third_table_x[-1], third_table_y_top - third_table_height)

        # Vertical lines
        for x in third_table_x:
            c.line(x, third_table_y_top, x, third_table_y_top - third_table_height)

        # Draw rotated text
        vertical_labels = ["Höhendifferenz in 100m*", "Horizontaldistanz", "Leistungskilometer**", "Marschszeit", "Distanz", "Leistungskilometer**", "Geplante Zeit", "Tatsächliche Zeit", "Pausen"]

        for i, label in enumerate(vertical_labels):
            x_left = third_table_x[i] + 18  # small left padding
            y_bottom = third_table_y_top - third_table_height + 4

            c.saveState()
            c.translate(x_left, y_bottom)
            c.rotate(90)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(0, 0, label)
            c.restoreState()
        
        # Draw main table
        c.grid(xlist, ylist[:len(rows) + 1]) # create number of rows
        
        # Draw second (single-column) grid
        c.grid(second_grid_xlist, ylist_second[:len(rows) + 1]) # create number of rows

        for row_index, row in enumerate(rows):
            y = ylist[row_index]
            num_cols = len(row)
            for col_index in range(num_cols):
                x = xlist[col_index]
                cell = row[col_index]
                text = str(cell)
                fontname = "Helvetica"
                fontsize = 9
                c.setFont(fontname, fontsize)

                text_y = y - row_height + (row_height - fontsize) / 2 + 2

                if col_index in text_columns_left_aligned:
                    c.drawString(x + 2, text_y, text)
                else:
                    text_width = c.stringWidth(text, fontname, fontsize)
                    cell_right_edge = xlist[col_index + 1]
                    c.drawString(cell_right_edge - text_width - 2, text_y, text)

                # Optional: fill in the second grid column with placeholder text
                # Draw text for the second column
                if row_index == 0:
                    # Multi-line styled header for the Bemerkung table using a TextObject
                    text_obj = c.beginText()
                    text_obj.setTextOrigin(second_grid_xlist[0] + 2, ylist_second[row_index] - row_height + 2)
                    text_obj.setFont("Helvetica-Bold", 9)
                    text_obj.textLine("BEMERKUNGEN")
                    text_obj.setFont("Helvetica", 9)
                    text_obj.textLine("* Höhenmeter direkt")
                    text_obj.textLine("  in Hektometer notieren")
                    text_obj.textLine("  (1 hm = 100 m)")
                    text_obj.textLine("** Leistungskilometer:")
                    text_obj.textLine("   Distanz (in km) +")
                    text_obj.textLine("   Steigung (in hm)")
                    c.drawText(text_obj)
                else:
                    bemerkung_text = str(bemerkung_data[row_index]) if row_index < len(bemerkung_data) else ""
                    text_y2 = ylist_second[row_index] - row_height + (row_height - fontsize) / 2 + 2
                    c.setFont("Helvetica", fontsize)
                    c.drawString(second_grid_xlist[0] + 2, text_y2, bemerkung_text)


        c.showPage()

    c.save()


# Prepare data outside the function
header = ("Ort, Flurname, Koordinaten", "Nr", "Höhe", "hm", "km", "Lkm", "h:mm", "km", "Lkm", "hh:mm", "hh:mm", "Pause")
data = [header]
for i in range(1, 31):
    ort = f"Station {i}"
    hoehe = randint(1000, 2000)
    hm = randint(-200, 200)
    km1 = round(uniform(0.1, 5.0), 1)
    lkm1 = round(km1 + abs(hm) / 100, 2)
    zeit1 = f"{randint(0,1)}:{randint(0,59):02d}"
    km2 = round(uniform(0.1, 5.0), 1)
    lkm2 = round(km2 + abs(hm) / 120, 2)
    zeit2 = f"{randint(0,1)}:{randint(0,59):02d}"
    gesamt = f"{randint(0,5)}:{randint(0,59):02d}"
    pause = f"{randint(0,0)}:{randint(1,15):02d}"
    data.append((ort, i, hoehe, hm, km1, lkm1, zeit1, km2, lkm2, zeit2, gesamt, pause))

bemerkung_data = ["Bemerkungen"]  # First entry is the header
for i in range(1, len(data)):
    if i % 5 == 0:
        bemerkung_data.append("Rastplatz mit Aussicht")
    elif i % 3 == 0:
        bemerkung_data.append("Weg schlecht markiert")
    else:
        bemerkung_data.append("–")

export_to_pdf(data)

pdf_path = "marschzeit-grid.pdf"
os.startfile(pdf_path)
