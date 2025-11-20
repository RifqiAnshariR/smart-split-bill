import os
import json
import requests
import pandas as pd
import streamlit as st
from config.config import Config
from utils.styling import load_css


BASE_URL = "http://fastapi:8000" if os.environ.get("DOCKER") else "http://localhost:8000"


st.set_page_config(
    page_title=f"{Config.APP_PAGE_TITLE} - Upload and Split",
    page_icon=Config.APP_PAGE_ICON,
    layout=Config.APP_LAYOUT,
    menu_items=Config.APP_MENU_ITEMS
)


load_css()


def show_items_data(session_state_key, disabled=False):
    df = pd.DataFrame(st.session_state.receipt_data[session_state_key])
    values = st.data_editor(
        df,
        num_rows="fixed",
        column_config={
            "name": st.column_config.TextColumn("Item Name"),
            "quantity": st.column_config.NumberColumn("Quantity", min_value=1, step=1),
            "price_per_unit": st.column_config.NumberColumn("Price per Unit", min_value=1, step=1),
        },
        hide_index=True,
        key=f"editor_{session_state_key}",
        disabled=disabled
    )
    st.session_state.receipt_data[session_state_key] = values.to_dict(orient="records")
    return values


def show_extras_data(*args, disabled=False):
    values = {}
    for label, session_state_key in args:
        value = st.number_input(
            label=label,
            min_value=0,
            value=int(st.session_state.receipt_data.get(session_state_key, 0)),
            step=1,
            key=f"input_{session_state_key}",
            disabled=disabled
        )
        st.session_state.receipt_data[session_state_key] = value
        values[session_state_key] = value
    return values


def show_total_price(items_data, extras_data, session_state_key):
    sub_total = sum(items_data["price_per_unit"] * items_data["quantity"])
    total = sub_total + extras_data['service_price'] + extras_data['tax_price'] - extras_data['discount_price']
    st.session_state.receipt_data[session_state_key] = total
    st.metric("Total Price", f"{total:,}")


def show_upload_page():
    st.subheader("Upload Receipt")

    with st.form(border=True, key="form_upload"):
        receipt_image = st.file_uploader("Upload Receipt", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        submit_upload = st.form_submit_button("Submit", key="btn_submit_upload", use_container_width=True)

        if submit_upload and receipt_image:
            files = {"file": (receipt_image.name, receipt_image, receipt_image.type)}

            with st.spinner("Extracting receipt data..."):
                response = requests.post(f"{BASE_URL}/upload-receipt", files=files)

            if response.status_code == 200:
                st.session_state.receipt_data = response.json()
                st.session_state.current_page = "receipt_data"
                st.rerun()
            else:
                st.error(response.text)


def show_receipt_data_page():
    st.subheader("Extracted Receipt Data")

    with st.container(border=True, key="container_receipt_data"):
        items_data = show_items_data('items')
        extras_data = show_extras_data(
            ("Service Price", "service_price"),
            ("Tax Price", "tax_price"),
            ("Discount Price", "discount_price")
        )
        show_total_price(items_data, extras_data, 'total_price')

    col1, col2 = st.columns(2, gap="small")
    with col1:
        if st.button("Split Evenly", key="btn_nav_split_evenly", use_container_width=True):
            st.session_state.current_page = "split_evenly"
            st.rerun()

    with col2:
        if st.button("Split By Items", key="btn_nav_split_by_items", use_container_width=True):
            st.session_state.current_page = "split_by_items"
            st.rerun()

    if st.button("Back", key="btn_nav_back_upload", use_container_width=True):
        st.session_state.pop("receipt_data", None)

        st.session_state.current_page = "upload"
        st.rerun()


def show_split_evenly_page():
    st.subheader("Extracted Receipt Data")

    with st.container(border=True, key="container_receipt_display"):
        items_data = show_items_data('items', disabled=True)
        extras_data = show_extras_data(
            ("Service Price", "service_price"),
            ("Tax Price", "tax_price"),
            ("Discount Price", "discount_price"),
            disabled=True
        )
        show_total_price(items_data, extras_data, 'total_price')

    st.subheader("Split Evenly")

    with st.container(border=True, key="container_split_evenly"):
        num_people = st.number_input("Number of people", min_value=1, step=1, key="input_num_people")

        st.metric("Amount per Person", f"{st.session_state.evenly_result:,}")

        if st.button("Calculate", key="btn_calculate_evenly", use_container_width=True):
            payload = {
                "receipt": st.session_state.receipt_data,
                "num_people": num_people,
            }
            response = requests.post(f"{BASE_URL}/split-evenly", json=payload)
            st.session_state.evenly_result = response.json()["result"]
            st.rerun()

    if st.button("Back", key="btn_nav_back_receipt", use_container_width=True):
        st.session_state.pop("evenly_result", None)

        st.session_state.current_page = "receipt_data"
        st.rerun()


def show_split_by_items_page():
    st.subheader("Extracted Receipt Data")

    with st.container(border=True, key="container_receipt_display_items"):
        items_data = show_items_data('items', disabled=True)
        extras_data = show_extras_data(
            ("Service Price", "service_price"),
            ("Tax Price", "tax_price"),
            ("Discount Price", "discount_price"),
            disabled=True
        )
        show_total_price(items_data, extras_data, 'total_price')

    st.subheader("Split By Items")

    with st.container(border=True, key="container_split_by_items"):
        assigned_quantities = {}
        for user_items in st.session_state.split_by_items_assignments.values():
            for name, quantity in user_items.items():
                assigned_quantities[name] = assigned_quantities.get(name, 0) + quantity

        for item in st.session_state.receipt_data["items"]:
            name = item["name"]
            quantity = item["quantity"]
            st.session_state.available_receipt_data[name] = quantity - assigned_quantities.get(name, 0)

        new_user = st.text_input("User", key="input_new_user", placeholder="Enter user")

        if st.button("Add User", key="btn_add_user"):
            new_user = new_user.strip()
            if new_user and new_user not in st.session_state.split_by_items_assignments:
                st.session_state.split_by_items_assignments[new_user] = {}
                st.rerun()

        receipt_items = [item["name"] for item in st.session_state.receipt_data["items"]]

        for user, items in st.session_state.split_by_items_assignments.items():
            with st.expander(user, expanded=True):
                col1, col2 = st.columns(spec=[3, 1])
                with col1:
                    selected_item = st.selectbox("Item", options=receipt_items, key=f"select_item_{user}")
                with col2:
                    quantity = st.number_input("Quantity", min_value=1, value=1, step=1, key=f"input_qty_{user}")

                if st.button("Add Item", key=f"btn_add_item_{user}"):
                    available = st.session_state.available_receipt_data.get(selected_item, 0)
                    if available < quantity:
                        st.error(f"Not enough '{selected_item}' available. (Remaining: {available})")
                    else:
                        st.session_state.split_by_items_assignments[user][selected_item] = quantity
                        st.rerun()

                if items:
                    st.write("Assigned:")
                    for name, quantity in items.items():
                        st.write(f"- {name} × {quantity}")

                if user in st.session_state.split_by_items_result:
                    amount = st.session_state.split_by_items_result[user]
                    st.metric("Total:", f"{amount:,}")

                if st.button(f"Delete User", key=f"btn_delete_user_{user}"):
                    st.session_state.split_by_items_assignments.pop(user, None)
                    st.session_state.split_by_items_result.pop(user, None)
                    st.rerun()

        if st.button("Calculate Split", key="btn_calc_split_items", use_container_width=True):
            payload = {
                "receipt": st.session_state.receipt_data,
                "assignments": st.session_state.split_by_items_assignments
            }

            try:
                response = requests.post(f"{BASE_URL}/split-by-items", json=payload)
                st.session_state.split_by_items_result = response.json()["result"]
                st.rerun()
            except Exception as e:
                st.error("Failed to calculate")

    if st.button("Back", key="btn_nav_back_receipt_items", use_container_width=True):
        st.session_state.pop("split_by_items_assignments", None)
        st.session_state.pop("split_by_items_result", None)
        st.session_state.pop("available_receipt_data", None)

        st.session_state.current_page = "receipt_data"
        st.rerun()


if "current_page" not in st.session_state:
    st.session_state.current_page = "upload"

if "receipt_data" not in st.session_state:
    st.session_state.receipt_data = None

if "evenly_result" not in st.session_state:
    st.session_state.evenly_result = 0

if "split_by_items_assignments" not in st.session_state:
    st.session_state.split_by_items_assignments = {}

if "split_by_items_result" not in st.session_state:
    st.session_state.split_by_items_result = {}
    
if "available_receipt_data" not in st.session_state:
    st.session_state.available_receipt_data = {}


st.title(Config.APP_PAGE_TITLE)

if st.session_state.current_page == "upload":
    show_upload_page()

elif st.session_state.current_page == "receipt_data" and st.session_state.get("receipt_data"):
    show_receipt_data_page()

elif st.session_state.current_page == "split_evenly":
    show_split_evenly_page()

elif st.session_state.current_page == "split_by_items":
    show_split_by_items_page()


st.html("<div class='footer'>©2025 Rifqi Anshari Rasyid.</div>")
