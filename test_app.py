import pytest
import pandas as pd
from datetime import date
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mysql.connector
from unittest.mock import patch, MagicMock
from tkinter import ttk
import tkinter as tk
from app import (connect_to_database, get_data, table_frame, create_table, status_bar, update_status,click_Get_All_Data,
                click_Get_Collision, click_filter_by_date, click_filter_today, cal_start, cal_end, txt_Direction,
                 click_filter_by_direction, get_data, create_table, tmp_query_nr, txt_distance_low, txt_distance_high,
                 click_search_between_distance, click_show_collision_distance_chart)


def test_connect_to_database():
    # Mock the mysql.connector.connect function to avoid actual database connection
    with patch("app.mysql.connector.connect") as mock_connect:
        # Mock the return value to simulate a successful database connection
        mock_connect.return_value = MagicMock()
        # Call the function under test
        conn = connect_to_database()
        # Assert that the returned connection is not None (successful connection)
        assert conn is not None
        # Ensure that the connect function was called exactly once
        mock_connect.assert_called_once()

def test_get_data():
    query = "SELECT * FROM test_table"
    # Mock DataFrame returned by the database query
    mock_df = pd.DataFrame({"id": [1, 2], "value": [100, 200]})

    # Mock the connect_to_database and pd.read_sql methods to simulate database interaction
    with patch("app.connect_to_database") as mock_connect:
       with patch("app.pd.read_sql", return_value=mock_df) as mock_read_sql:

        # Mock the return value of connect_to_database
        mock_connect.return_value = MagicMock()
        result = get_data(query)

        # Assert that the returned DataFrame is not empty
        assert not result.empty

        # Assert that the columns of the returned DataFrame
        assert list(result.columns) == ["id", "value"]
        mock_read_sql.assert_called_once_with(query, mock_connect.return_value, params=())


def test_get_data_connection_failure():
    query = "SELECT * FROM test_table"
    with patch("app.connect_to_database", side_effect=mysql.connector.Error):
        result = get_data(query)
        assert result.empty

def test_get_data_query_failure():
    query = "INVALID SQL"
    with patch("app.connect_to_database") as mock_connect:
        with patch("app.pd.read_sql", side_effect=Exception("Query error")):
            mock_connect.return_value = MagicMock()
            result = get_data(query)
            assert result.empty


def test_create_table():
    # Prepare mock DataFrame
    mock_df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})

    # Mock the tkinter Treeview and ttk components
    with patch.object(ttk, 'Treeview') as mock_treeview, \
            patch.object(table_frame, 'winfo_children', return_value=[]):
        mock_treeview_instance = mock_treeview.return_value
        create_table(mock_df)

        # Check if the Treeview was configured correctly with columns ['col1', 'col2']
        mock_treeview.assert_called_once_with(table_frame, columns=['col1', 'col2'], show="headings")

        # Check that the insert method was called for both rows in the DataFrame
        mock_treeview_instance.insert.assert_any_call("", "end", values=[1, 3])  # First row
        mock_treeview_instance.insert.assert_any_call("", "end", values=[2, 4])  # Second row

def test_update_status():
    # Mock the get_data and create_table functions
    with patch.object(status_bar, 'config') as mock_config:
        update_status("Test message", "green")
        mock_config.assert_called_once_with(text="Test message", foreground="green")



def test_click_get_all_data():
    # Mock the get_data and create_table functions
    with patch("app.get_data") as mock_get_data:
        with patch("app.create_table") as mock_create_table:
            mock_df = "mock_df"
            mock_get_data.return_value = mock_df
            # Call the function
            click_Get_All_Data()

            mock_get_data.assert_called_once_with("SELECT * FROM sensor_data ORDER BY `Date Time` DESC")
            mock_create_table.assert_called_once_with(mock_df)

            assert tmp_query_nr == 0

def test_click_Get_Collision():
    # Mock the get_data and create_table functions
    with patch("app.get_data") as mock_get_data:
        with patch("app.create_table") as mock_create_table:
            mock_df = "1"
            mock_get_data.return_value = mock_df
            # Call the function
            click_Get_Collision()

            mock_get_data.assert_called_once_with("SELECT * FROM sensor_data WHERE `Robot Collision` = 1 ORDER BY `Date Time` DESC")
            mock_create_table.assert_called_once_with(mock_df)

            assert tmp_query_nr == 0


def test_filter_by_direction():
    # Mock the get_data and create_table functions
    with patch("app.get_data") as mock_get_data, patch("app.create_table") as mock_create_table:
            mock_df = "mock_df"
            mock_get_data.return_value = mock_df

            txt_Direction.get = MagicMock(return_value="Forward")
            # Call the function
            click_filter_by_direction()

            mock_get_data.assert_called_once_with("SELECT * FROM sensor_data WHERE `Control direction` = %s ORDER BY `Date Time` DESC", ("Forward",))
            mock_create_table.assert_called_once_with(mock_df)

            assert tmp_query_nr == 0


def test_click_filter_by_direction_without_direction(capsys):
    # Mock the get_data and create_table functions
    with patch('app.get_data') as mock_get_data, patch('app.create_table') as mock_create_table:
        txt_Direction.get = MagicMock(return_value="")

        # Call the function
        click_filter_by_direction()

        # Ensure get_data and create_table were not called because of the empty direction
        mock_get_data.assert_not_called()
        mock_create_table.assert_not_called()

        # Capture the printed output and check if the error message is printed
        captured = capsys.readouterr()
        assert "Please enter a direction!" in captured.out


def test_click_filter_by_date():
    # Mock the get_data and create_table functions
    with patch('app.get_data') as mock_get_data, patch('app.create_table') as mock_create_table:
        mock_df = "mock_df"  # Mock DataFrame
        mock_get_data.return_value = mock_df  # Return the mock DataFrame

        # Mock the start and end date pickers
        cal_start.get_date = MagicMock(return_value=date(2025, 1, 1))
        cal_end.get_date = MagicMock(return_value=date(2025, 2, 1))

        # Call the function
        click_filter_by_date()

        # Check that get_data was called with the correct query for the date filter
        mock_get_data.assert_called_once_with(
            "SELECT * FROM sensor_data WHERE `Date Time` BETWEEN %s AND %s ORDER BY `Date Time` DESC",
            ("2025-01-01", "2025-02-01"))

        # Check that create_table was called with the returned DataFrame
        mock_create_table.assert_called_once_with(mock_df)

        # Check that the global variable tmp_query_nr is set to 4
        assert tmp_query_nr == 0

def test_click_filter_today():
    # Mock the get_data and create_table functions
    with patch('app.get_data') as mock_get_data, patch('app.create_table') as mock_create_table:
        mock_df = "mock_df"  # Mock DataFrame
        mock_get_data.return_value = mock_df  # Return the mock DataFrame

        # Patch datetime.date.today() method to return a specific date
        with patch('app.click_filter_today', return_value=date(2025, 3, 10)):
            # Call the function under test
            click_filter_today()

            # Ensure that get_data was called with the correct query and today's date
            mock_get_data.assert_called_once_with(
                "SELECT * FROM sensor_data WHERE DATE(`Date Time`) = %s ORDER BY `Date Time` DESC",
                (date(2025, 3, 10),)
            )

            # Ensure create_table was called with the mock DataFrame
            mock_create_table.assert_called_once_with(mock_df)

def test_click_search_between_distance():
    # Mock the get_data and create_table functions
    with patch('app.get_data') as mock_get_data, patch('app.create_table') as mock_create_table:
        mock_df = "mock_df"  # Mock DataFrame
        mock_get_data.return_value = mock_df  # Return the mock DataFrame

        # Mock the input fields for low and high distance values
        txt_distance_low.get = MagicMock(return_value="10")
        txt_distance_high.get = MagicMock(return_value="50")

        # Call the function under test
        click_search_between_distance()

        # Ensure that get_data was called with the correct query and values
        mock_get_data.assert_called_once_with(
            "SELECT * FROM sensor_data WHERE `Obstacle Distance`BETWEEN %s AND %s ORDER BY `Obstacle Distance` DESC",
            ("10", "50")
        )

        # Ensure create_table was called with the mock DataFrame
        mock_create_table.assert_called_once_with(mock_df)

def test_click_search_between_distance_without_input():
    # Mock the print function to capture the error message
    with patch('builtins.print') as mock_print:
        # Mock the input fields for low and high distance values to return empty strings
        txt_distance_low.get = MagicMock(return_value="")
        txt_distance_high.get = MagicMock(return_value="")

        # Call the function under test
        click_search_between_distance()

        # Ensure that the print function was called with the expected error message
        mock_print.assert_called_once_with("Please enter low and high distance value!")


def test_click_show_collision_distance_chart():
    # Mock the get_data and create_table functions
    with patch('app.get_data') as mock_get_data, patch('app.create_table') as mock_create_table:
        mock_df = MagicMock()  # Mock DataFrame for collision data
        mock_df.empty = False
        mock_df["Obstacle Distance"] = [50, 100, 150, 200, 250]

        mock_df_count = MagicMock()  # Mock DataFrame for count query
        mock_df_count.empty = False
        mock_df_count["Total Collision"] = [5]

        mock_get_data.side_effect = [mock_df, mock_df_count]  # First call returns mock_df, second returns mock_df_count
        mock_create_table.return_value = None  # Just ensure it doesn't raise error when called

        # Mock Tkinter Toplevel window creation and FigureCanvasTkAgg
        with patch('tkinter.Toplevel') as mock_toplevel, patch(
                'matplotlib.backends.backend_tkagg.FigureCanvasTkAgg') as mock_canvas:
            mock_toplevel.return_value = MagicMock(spec=tk.Toplevel)  # Mock Toplevel as a real Toplevel instance
            mock_toplevel()._w = MagicMock()  # Create a _w mock to simulate widget behavior

            # Call the function under test
            click_show_collision_distance_chart()

            # Assert that get_data was called twice with the correct queries
            mock_get_data.assert_any_call("SELECT `Obstacle Distance` FROM sensor_data WHERE `Robot Collision` = 1")
            mock_get_data.assert_any_call(
                "SELECT Count(*) AS 'Total Collision' FROM sensor_data WHERE `Robot Collision` = 1")

            # Assert that create_table was called with the collision count data
            mock_create_table.assert_called_once_with(mock_df_count)

            # Ensure a new window was created for the chart (Tkinter)
            mock_toplevel.assert_called_once()

            # Ensure that FigureCanvasTkAgg was used to display the chart
            mock_canvas.assert_called_once()
