# This ile is in the src folder
from random import randint, uniform
import os
from PIL import Image
from reportlab.lib.utils import ImageReader
from itertools import islice
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, A3
from reportlab.lib.units import inch
import geopandas as gpd
from shapely.geometry import Point
from src.maps import generate_elevation_plot
from reportlab.lib.utils import ImageReader
from io import BytesIO
# from import_gpx import import_gpx
# from calculate import calc_leistungskm
# import geopandas as gpd
# import pandas as pd
from datetime import timedelta
from src.maps import draw_scaled_image

# More Dummy data for testing
# filename = "marschzeit-grid.pdf"                                    # exists
# titel = "Crazy Routenname: HIER KÖNNTE IHRE WERBUNG STEHEN"    # exists
# geschwindigkeit = 4                    # exists
# tot_dist = 10.5                     # exists not implemented
# tot_hm_pos = 500                    # exists
# tot_hm_neg = 300                    # exists
# tot_marschzeit_h = 2                # exists
# tot_marschzeit_min = 30             # exists
# ersteller = "Alex & Ignazio"        # exists
# erstellerdatum = "11.09.2001"                # exists not implemented
# #gdf erzeugen

# gpx = import_gpx("C:/Users/alexa/GrSchmeterling_Hackathon/data/7-gipfel-tour-flumserberg.gpx")
# gdf_calc_t = calc_leistungskm(gpx)


# df = gdf_calc_t[0]  # get the DataFrame from the tuple

# gdf_calc = pd.DataFrame({
#     'Abschnitt': df['segment_id'],
#     'Von': df['von_pkt_name'],
#     'Nach': df['bis_pkt_name'],
#     'Laenge [km]': df['cumulative_km'].round(2),
#     'Hoehenmeter [m]': df['elevation'].round(1),
#     'Leistungskm': df['Leistungskm [km]'].round(2),
#     'Marschzeit [min]': df['Marschzeit [min]'].round(0),
#     'Hinweis': ""  # Add an empty 'Hinweis' column
# })

# Daten von main.py

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
    
    header = ("Ort, Flurname, Koordinaten", "Nr", "Höhe", "hm", "km", "Lkm", "h:mm", "km", "Lkm", "h:mm", "h:mm", "h:mm")
    data = [header]
# ['segment_id', 'von_pkt_name', 'von_pkt_geom', 'bis_pkt_name', 'bis_pkt_geom', 
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

    c = canvas.Canvas(filename, pagesize=A4)
    w, h = A4
    max_rows_per_page = 45

    # Layout settings
    x_offset = 20
    y_offset = 250
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
        top_table_values = ["erstellt von:", f"{ersteller}"]
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
        top_table_values = ["Route:", titel, "Geschwindigkeitsfaktor:" ]
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
        top_table_values = ["Zwischenwerte", "Gesamtsummen", f"{geschwindigkeit} (Lkm/h)"]
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
            c.setFont("Helvetica-Bold", 9)
            c.drawString(0, 0, label)
            c.restoreState()
        
        # Draw main table
        c.grid(xlist, ylist[:len(rows) + 1]) # create number of rows

        # --- Eighth table: 1 row, 3 columns, below main table ---
        bottom_table_col_widths = [112, 112, 112, 112, 112]
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
            c.setFont("Helvetica", 9)
            text_width = c.stringWidth(text, "Helvetica", 9)
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

        draw_scaled_image(
            c,
            "C://temp_schmetterling/elevation.png",
            x=40,
            y=bottom_table_y_bottom - 200,  # Dynamisch angepasst: genug Platz
            max_width=550
        )

        c.showPage()
        # Start page numbr 2
        # text = c.beginText(20, h - 20)  # Create a text object at (x=20, y=h - 20)
        # text.setFont("Helvetica", 9)


        # Größe abfragen
        draw_scaled_image(c, "C://temp_schmetterling/map.png", x=-50, y=200, max_width=1700)
        c.showPage()

        # if os.path.exists(image_path):
        #     os.remove(image_path)

        # if os.path.exists(image_path2):
        #     os.remove(image_path2)

        # path = "C://temp_schmetterling"
        # if os.path.exists(path):
        #     os.rmdir(path)

    c.save()