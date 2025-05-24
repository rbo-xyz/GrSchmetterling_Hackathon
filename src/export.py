import os
from reportlab.lib.utils import ImageReader
from itertools import islice
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5, A4, A3, A2, A1, A0, B0, B1, B2, B3, B4
from reportlab.lib.utils import ImageReader
from datetime import timedelta
from src.maps import draw_scaled_image

# String to Page sizes
PAGE_SIZES = {
    "A0": A0,
    "A1": A1,
    "A2": A2,
    "A3": A3,
    "A4": A4,
    "A5": A5,
    "B0": B0,
    "B1": B1,
    "B2": B2,
    "B3": B3,
    "B4": B4,   
}

# font size
base_font_size = 9
base_height = 841.89  # A4 height in points

def get_page_size(format_str):
    return PAGE_SIZES.get(format_str.upper(), A2)

def get_scaled_centered_image_params(path, page_width, page_height, max_width_ratio=0.8, max_height_ratio=0.6):
    img = ImageReader(path)
    img_width, img_height = img.getSize()

    max_width = page_width * max_width_ratio
    max_height = page_height * max_height_ratio

    scale = min(max_width / img_width, max_height / img_height)

    draw_width = img_width * scale
    draw_height = img_height * scale

    x = (page_width - draw_width) / 2
    y = (page_height - draw_height) / 2

    return x, y, draw_width, draw_height

def grouper(iterable, n):
    it = iter(iterable)
    while True:
        chunk = list(islice(it, n))
        if not chunk:
            break
        yield chunk

def export_to_pdf(
    gdf_calc,
    filename,
    geschwindigkeit,
    tot_dist,
    tot_lkm,
    tot_hm_pos,
    tot_hm_neg,
    tot_marschzeit_h,
    tot_marschzeit_min,
    titel,
    ersteller,
    erstellerdatum,
    export_format
):
    page_format_str = export_format
    export_format = get_page_size(page_format_str)

    header = ("Ort, Flurname, Koordinaten", "Nr", "Höhe", "hm", "km", "Lkm", "h:mm", "km", "Lkm", "h:mm", "h:mm", "h:mm")
    data = [header]
    #  ['segment_id', 'von_pkt_name', 'von_pkt_geom', 'bis_pkt_name', 'bis_pkt_geom', 
    #  'segment_geom', 'cumulative_km', 'elevation', 'Leistungskm [km]', 'Marschzeit [min]']
    dist_moment = 0
    lkm_moment = 0
    time_moment = 0
    for i, row in gdf_calc.iterrows():
        ort = row.get("von_pkt_name", f"Abschnitt {i+1}")
        nr = row.get("segment_id", i + 1)  # Fallback auf Index+1
        hoehe = row.get("von_pkt_geom", i+1)
        hm = row.get("elevation", "")  # Annahme: elevation = Höhenmeter
        km = round(row.get("cumulative_km", 0), 2)
        lkm = round(row.get("Leistungskm [km]", 0), 2)

        hoehe = int(round(hoehe.z,0))
        dist_moment = dist_moment + km
        lkm_moment = lkm_moment + lkm

        dist_moment = round(dist_moment, 2)
        lkm_moment = round(lkm_moment, 2)

        # Marschzeit als hh:mm
        marschzeit_min = int(row.get("Marschzeit [min]", 0))
        zeit_str = str(timedelta(minutes=marschzeit_min))[:-3]  # 'hh:mm'

        time_moment = time_moment + marschzeit_min
        zeit_str_moment = str(timedelta(minutes=time_moment))[:-3]  # 'hh:mm'

        pause = row.get("Hinweis", "")  # Hinweis existiert evtl. nicht

        data.append((ort, nr, hoehe, hm, km, lkm, zeit_str, dist_moment, lkm_moment, zeit_str_moment, "", pause))

    c = canvas.Canvas(filename, pagesize=export_format)
    w, h = export_format
    max_rows_per_page = 45
    #dynamic font size
    font_size = int(h / base_height * base_font_size)
    # Layout settings
    x_offset = w * 0.035
    y_offset = h * 0.3
    row_height = h * 0.02

    third_table_height = row_height * 7  # Height of the third table

    # Table column widths
    col_widths = [w * 0.22, w * 0.035, w * 0.05, w * 0.05, w * 0.05, w * 0.05, w * 0.05,
                   w * 0.05, w * 0.05, w * 0.06, w * 0.06, w * 0.05]

                    # first 3 important 

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
    second_grid_width = w * 0.17
    second_grid_xlist = [second_grid_x_start, second_grid_x_start + second_grid_width]

    text_columns_left_aligned = [0, 12]  # "Ort" and "Bemerkung"

    third_table_y_top = ylist[0] + third_table_height

    for rows in grouper(data, max_rows_per_page):
        rows = tuple(filter(bool, rows))

        # --- sixth table ---
        top_table_col_widths = [w * 0.1, w * 0.205]  # adjustable
        top_table_x = [x_offset]  # start at the left side
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
        top_table_values = ["erstellt von:", f"{ersteller}"]
        for i, text in enumerate(top_table_values):
            lines = text.split("\n")
            x_left = top_table_x[i]
            x_right = top_table_x[i + 1]
            cell_center_x = (x_left + x_right) / 2

            c.setFont("Helvetica", font_size)
            total_text_height = len(lines) * 10  # approx line height = 10
            start_y = top_table_y_bottom + (top_table_row_height + total_text_height) / 2 - 10

            for j, line in enumerate(lines):
                text_width = c.stringWidth(line, "Helvetica", font_size)
                c.drawString(cell_center_x - text_width / 2, start_y - j * 10, line)
    
        # --- seventh table (1 column, 2 rows, same position as sixth) ---
        seventh_table_col_width = w * 0.305  # adjustable width
        seventh_table_x = [x_offset, x_offset + seventh_table_col_width]

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
        seventh_table_values = ["Landeskarten:", 
                                "Alexs Landeskarte (jetzt mit mehr Eiern)"]
        for row_index, text in enumerate(seventh_table_values):
            c.setFont("Helvetica", font_size)
            text_width = c.stringWidth(text, "Helvetica", font_size)
            
            # Horizontal center between the two vertical lines
            cell_center_x = (seventh_table_x[0] + seventh_table_x[1]) / 2

            # Get current row height (first is row_height, second is row_height * 3)
            row_height_current = seventh_table_row_heights[row_index]

            # Calculate vertical center of the row
            row_bottom = seventh_table_y[row_index + 1]
            text_y = row_bottom + (row_height_current - 9) / 2  # 9 is font size

            # Draw centered text
            c.drawString(cell_center_x - text_width / 2, text_y, text)

        # --- fifth table ---
        top_table_col_widths = [w * 0.1, w * 0.675, w * 0.17]  # adjustable
        top_table_x = [x_offset]  # start at the left side
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
        top_table_values = ["Route:", titel, 
                            "Geschwindigkeitsfaktor:" ]
        for i, text in enumerate(top_table_values):
            x = top_table_x[i]
            c.setFont("Helvetica", font_size)
            text_width = c.stringWidth(text, "Helvetica", font_size)
            cell_center = (top_table_x[i] + top_table_x[i + 1]) / 2
            c.drawString(cell_center - text_width / 2, top_table_y_bottom + 4, text)

        # --- fouth table ---
        top_table_col_widths = [w * 0.2, w * 0.27, w * 0.17]  # second row
        top_table_x = [x_offset + w * 0.305]  # start at the end of the main table
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
        top_table_values = ["Zwischenwerte", 
                            "Gesamtsummen", f"{geschwindigkeit} (Lkm/h)"]
        for i, text in enumerate(top_table_values):
            x = top_table_x[i]
            c.setFont("Helvetica", font_size)
            text_width = c.stringWidth(text, "Helvetica", font_size)
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
        vertical_labels = ["Höhendifferenz", 
                           "Horizontaldistanz", 
                           "Leistungskilometer*", 
                           "Marschszeit", 
                           "Distanz", 
                           "Leistungskilometer*", 
                           "Geplante Zeit", 
                           "Tatsächliche Zeit", 
                           "Pausen"]

        for i, label in enumerate(vertical_labels):
            x_left = third_table_x[i] + 18  # small left padding
            y_bottom = third_table_y_top - third_table_height + 4

            c.saveState()
            c.translate(x_left, y_bottom)
            c.rotate(90)
            c.setFont("Helvetica-Bold", font_size)
            c.drawString(0, 0, label)
            c.restoreState()
        
        # Draw main table
        c.grid(xlist, ylist[:len(rows) + 1]) # create number of rows

        # --- Eighth table: 1 row, 3 columns, below main table ---
        bottom_table_col_widths = [w * 0.189, w * 0.189, w * 0.189, w * 0.189, w * 0.189]
        bottom_table_x = [xlist[0]]
        for width in bottom_table_col_widths:
            bottom_table_x.append(bottom_table_x[-1] + width)

        # Y-position: a bit below the last y-row of the main table
        bottom_table_y_top = ylist[len(rows)]
        bottom_table_y_bottom = bottom_table_y_top - row_height

        # Horizontal lines
        c.line(bottom_table_x[0], bottom_table_y_top, bottom_table_x[-1], bottom_table_y_top)
        c.line(bottom_table_x[0], bottom_table_y_bottom, bottom_table_x[-1], bottom_table_y_bottom)

        # Vertical lines
        for x in bottom_table_x:
            c.line(x, bottom_table_y_top, x, bottom_table_y_bottom)

        # Dummy text for cells
        bottom_table_values = [f"Zeit ohne Pausen: {tot_marschzeit_h}:{tot_marschzeit_min} h",
                                f"Pos. Höhendiff: {tot_hm_pos} m",
                                  f"Neg. Höhendiff: {tot_hm_neg} m",
                                   f"Tot. Distanz: {tot_dist}",
                                    f"Tot. Lkm: {tot_lkm}"]
        for i, text in enumerate(bottom_table_values):
            x_left = bottom_table_x[i]
            x_right = bottom_table_x[i + 1]
            cell_center = (x_left + x_right) / 2
            c.setFont("Helvetica", font_size)
            text_width = c.stringWidth(text, "Helvetica", font_size)
            c.drawString(cell_center - text_width / 2, bottom_table_y_bottom + 4, text)

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
                fontsize = font_size
                c.setFont(fontname, fontsize)

                text_y = y - row_height + (row_height - fontsize) / 2 + 2

                if col_index in text_columns_left_aligned:
                    c.drawString(x + 2, text_y, text)
                else:
                    text_width = c.stringWidth(text, fontname, fontsize)
                    cell_right_edge = xlist[col_index + 1]
                    c.drawString(cell_right_edge - text_width - 2, text_y, text)

                # Draw text for the second column
                if row_index == 0:
                    # Multi-line styled header for the Bemerkung table using a TextObject
                    text_obj = c.beginText()
                    text_obj.setTextOrigin(second_grid_xlist[0] + 2, ylist_second[row_index] - row_height + 2)
                    text_obj.setFont("Helvetica", font_size + 1)
                    text_obj.textLine("BEMERKUNGEN")
                    text_obj.setFont("Helvetica", font_size)
                    text_obj.textLine("* Leistungskilometer:")
                    text_obj.textLine("   Distanz (in km) +")
                    text_obj.textLine("   Steigung (in hm)")
                    c.drawText(text_obj)
                else:
                    bemerkung_text = ""
                    text_y2 = ylist_second[row_index] - row_height + (row_height - fontsize) / 2 + 2
                    c.setFont("Helvetica", fontsize)
                    c.drawString(second_grid_xlist[0] + 2, text_y2, bemerkung_text)

        bottom_table_y_bottom = ylist[len(rows)] - row_height  # Etwas Puffer

        x, y, draw_width, draw_height = get_scaled_centered_image_params(
            "C://temp_schmetterling/elevation.png", w, h)

        c.drawImage("C://temp_schmetterling/elevation.png", x, y = bottom_table_y_bottom - h * 0.24, width=draw_width, height=draw_height)

        c.showPage()

        # Größe abfragen
        x, y, draw_width, draw_height = get_scaled_centered_image_params(
            "C://temp_schmetterling/map.png", w, h)
        c.drawImage("C://temp_schmetterling/map.png", x - draw_width / 2, y - draw_width / 2, width=draw_width * 2, height=draw_height * 2)

        # if os.path.exists(image_path):
        #     os.remove(image_path)

        # if os.path.exists(image_path2):
        #     os.remove(image_path2)

        # path = "C://temp_schmetterling"
        # if os.path.exists(path):
        #     os.rmdir(path)

    c.save()