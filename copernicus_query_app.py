#!/usr/bin/env python3
"""
Streamlit Web UI for Copernicus Data Space Product Query
Similar to Swagger UI - Interactive API interface for querying Sentinel products
"""

import streamlit as st
import requests
from datetime import datetime, date
import io

# Configure page
st.set_page_config(
    page_title="Copernicus Product Query",
    page_icon="🛰️",
    layout="wide"
)

# Constants
ODATA_API_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"

PRODUCT_CONFIGS = {
    'sentinel2_l2a': {
        'name': 'Sentinel-2 L2A',
        'collection': 'SENTINEL-2',
        'product_type': 'S2MSI2A',
        'instrument': 'MSI',
        'description': 'MSI Level-2A Bottom of Atmosphere Reflectance',
        'requires_tile': True
    },
    'sentinel3_olci_l1_efr': {
        'name': 'Sentinel-3 OLCI L1 EFR',
        'collection': 'SENTINEL-3',
        'product_type': 'OL_1_EFR___',
        'instrument': 'OLCI',
        'description': 'OLCI Level-1 Full Resolution',
        'requires_tile': False
    },
    'sentinel3_slstr_l1_rbt': {
        'name': 'Sentinel-3 SLSTR L1 RBT',
        'collection': 'SENTINEL-3',
        'product_type': 'SL_1_RBT___',
        'instrument': 'SLSTR',
        'description': 'SLSTR Level-1 Radiances and Brightness Temperatures',
        'requires_tile': False
    },
    'sentinel1_grd': {
        'name': 'Sentinel-1 GRD',
        'collection': 'SENTINEL-1',
        'product_type': 'GRD',
        'instrument': 'SAR',
        'description': 'SAR Ground Range Detected',
        'requires_tile': False
    }
}

def build_odata_filter(config, bbox, start_date, end_date, tile=None):
    """Build OData filter string"""
    collection_filter = f"Collection/Name eq '{config['collection']}'"
    
    # Spatial filter
    bbox_polygon = (
        f"POLYGON(("
        f"{bbox['west']} {bbox['south']},"
        f"{bbox['east']} {bbox['south']},"
        f"{bbox['east']} {bbox['north']},"
        f"{bbox['west']} {bbox['north']},"
        f"{bbox['west']} {bbox['south']}"
        f"))"
    )
    spatial_filter = f"OData.CSC.Intersects(area=geography'SRID=4326;{bbox_polygon}')"
    
    # Collection-specific filters
    if config['collection'] == 'SENTINEL-2':
        type_filter = (
            f"Attributes/OData.CSC.StringAttribute/any("
            f"att:att/Name eq 'productType' and "
            f"att/OData.CSC.StringAttribute/Value eq '{config['product_type']}'"
            f")"
        )
        if tile:
            tile_filter = f"contains(Name,'{tile}')"
            odata_filter = f"{collection_filter} and {type_filter} and {tile_filter} and {spatial_filter}"
        else:
            odata_filter = f"{collection_filter} and {type_filter} and {spatial_filter}"
    else:
        instrument_filter = (
            f"Attributes/OData.CSC.StringAttribute/any("
            f"att:att/Name eq 'instrumentShortName' and "
            f"att/OData.CSC.StringAttribute/Value eq '{config['instrument']}'"
            f")"
        )
        name_filter = f"contains(Name,'{config['product_type']}')"
        odata_filter = f"{collection_filter} and {instrument_filter} and {name_filter} and {spatial_filter}"
    
    # Temporal filter
    start_time = f"{start_date}T00:00:00.000Z"
    end_time = f"{end_date}T23:59:59.999Z"
    temporal_filter = f"ContentDate/Start ge {start_time} and ContentDate/Start le {end_time}"
    odata_filter = f"{odata_filter} and {temporal_filter}"
    
    return odata_filter

def search_products(odata_filter, max_products=None, progress_callback=None):
    """Search products via OData API"""
    params = {
        "$filter": odata_filter,
        "$orderby": "ContentDate/Start asc",
        "$top": min(max_products, 1000) if max_products else 1000,
        "$expand": "Attributes"
    }
    
    all_products = []
    
    try:
        response = requests.get(ODATA_API_URL, params=params, timeout=120)
        response.raise_for_status()
        result = response.json()
        products = result.get('value', [])
        all_products.extend(products)
        
        if progress_callback:
            progress_callback(f"Found {len(products)} products in initial query")
        
        # Handle pagination
        next_link = result.get('@odata.nextLink')
        page_count = 1
        
        while next_link and (max_products is None or len(all_products) < max_products):
            page_count += 1
            if progress_callback:
                progress_callback(f"Fetching page {page_count}... (total so far: {len(all_products)})")
            
            response = requests.get(next_link, timeout=120)
            response.raise_for_status()
            result = response.json()
            products = result.get('value', [])
            
            if max_products:
                remaining = max_products - len(all_products)
                products = products[:remaining]
            
            all_products.extend(products)
            next_link = result.get('@odata.nextLink')
        
        return all_products
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"Error: {str(e)}")
        return []

def extract_product_info(products):
    """Extract product information including S3Path"""
    product_list = []
    
    for product in products:
        product_name = product.get('Name', '')
        
        # Extract acquisition date
        content_date = product.get('ContentDate', {})
        start_str = content_date.get('Start', '')
        if start_str:
            acquisition_date = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
        else:
            acquisition_date = None
        
        # Extract S3Path
        s3_path = None
        if 'Attributes' in product and product['Attributes']:
            for attr in product['Attributes']:
                if attr.get('Name') == 'S3Path':
                    s3_path = attr.get('Value')
                    break
        
        if not s3_path and 'S3Path' in product:
            s3_path = product['S3Path']
        
        size = product.get('ContentLength', 0)
        
        product_list.append({
            'product_name': product_name,
            'acquisition_date': acquisition_date,
            'datetime': start_str,
            'online': product.get('Online', False),
            'size_bytes': size,
            'size_mb': round(size / (1024 * 1024), 2) if size else 0,
            's3_path': s3_path
        })
    
    product_list.sort(key=lambda x: x['acquisition_date'] if x['acquisition_date'] else datetime.min)
    return product_list

# UI Layout
st.title("🛰️ Copernicus Data Space Product Query")
st.markdown("Interactive UI for querying and downloading Sentinel product lists")

# Sidebar for configuration
with st.sidebar:
    st.header("Query Configuration")
    
    # Product selection
    product_key = st.selectbox(
        "Product Type",
        options=list(PRODUCT_CONFIGS.keys()),
        format_func=lambda x: PRODUCT_CONFIGS[x]['name'],
        help="Select the Sentinel product type to query"
    )
    
    product_config = PRODUCT_CONFIGS[product_key]
    
    st.info(f"**{product_config['description']}**\n\n"
            f"Collection: {product_config['collection']}\n\n"
            f"Instrument: {product_config['instrument']}")
    
    # Tile input (for Sentinel-2)
    tile = None
    if product_config['requires_tile']:
        tile = st.text_input(
            "Tile ID",
            value="T32TPS",
            help="MGRS tile identifier (e.g., T32TPS)",
            placeholder="T32TPS"
        )
    
    st.markdown("---")
    
    # Spatial extent
    st.subheader("Spatial Extent")
    
    # Preset locations
    preset = st.selectbox(
        "Preset Location",
        options=["Custom", "Bolzano/South Tyrol", "Clear"],
        help="Select a preset location or use custom coordinates"
    )
    
    if preset == "Bolzano/South Tyrol":
        default_west = 11.46309533
        default_south = 46.28795898
        default_east = 11.75355181
        default_north = 46.40587491
    else:
        default_west = 0.0
        default_south = 0.0
        default_east = 0.0
        default_north = 0.0
    
    col1, col2 = st.columns(2)
    with col1:
        west = st.number_input("West (°)", value=default_west, format="%.6f")
        south = st.number_input("South (°)", value=default_south, format="%.6f")
    with col2:
        east = st.number_input("East (°)", value=default_east, format="%.6f")
        north = st.number_input("North (°)", value=default_north, format="%.6f")
    
    st.markdown("---")
    
    # Temporal extent
    st.subheader("Temporal Extent")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=date(2017, 9, 1),
            help="Start date for product search"
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=date(2020, 9, 30),
            help="End date for product search"
        )
    
    st.markdown("---")
    
    # Additional options
    st.subheader("Options")
    max_products = st.number_input(
        "Max Products",
        min_value=1,
        max_value=10000,
        value=None,
        help="Limit number of products (leave empty for all)"
    )

# Main content area
tab1, tab2, tab3 = st.tabs(["🔍 Query", "📊 Results", "ℹ️ API Info"])

with tab1:
    st.header("Execute Query")
    
    # Display query configuration
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Product", product_config['name'])
    with col2:
        st.metric("Collection", product_config['collection'])
    with col3:
        if tile:
            st.metric("Tile", tile)
    
    # Build filter preview
    if west != 0 or east != 0 or south != 0 or north != 0:
        bbox = {'west': west, 'south': south, 'east': east, 'north': north}
        odata_filter = build_odata_filter(
            product_config, 
            bbox, 
            start_date.isoformat(), 
            end_date.isoformat(),
            tile
        )
        
        with st.expander("🔧 View OData Filter"):
            st.code(odata_filter, language="text")
    
    # Query button
    if st.button("🚀 Execute Query", type="primary", use_container_width=True):
        if west == 0 and east == 0 and south == 0 and north == 0:
            st.error("Please specify a valid bounding box")
        else:
            # Execute query
            with st.spinner("Querying Copernicus Data Space..."):
                progress_container = st.empty()
                
                def progress_update(msg):
                    progress_container.info(msg)
                
                products = search_products(
                    odata_filter, 
                    max_products=max_products,
                    progress_callback=progress_update
                )
                
                if products:
                    st.success(f"✅ Found {len(products)} products!")
                    
                    # Extract info
                    product_list = extract_product_info(products)
                    
                    # Store in session state
                    st.session_state['products'] = product_list
                    st.session_state['query_config'] = {
                        'product': product_config['name'],
                        'collection': product_config['collection'],
                        'bbox': bbox,
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'tile': tile
                    }
                    
                    st.info("📊 Switch to 'Results' tab to view and download products")
                else:
                    st.warning("No products found matching your criteria")

with tab2:
    st.header("Query Results")
    
    if 'products' in st.session_state and st.session_state['products']:
        products = st.session_state['products']
        config = st.session_state.get('query_config', {})
        
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Products", len(products))
        with col2:
            total_size_gb = sum(p['size_bytes'] for p in products) / (1024**3)
            st.metric("Total Size", f"{total_size_gb:.2f} GB")
        with col3:
            dates = [p['acquisition_date'] for p in products if p['acquisition_date']]
            if dates:
                st.metric("Date Range", f"{min(dates).date()} to {max(dates).date()}")
        with col4:
            online_count = sum(1 for p in products if p['online'])
            st.metric("Online", f"{online_count}/{len(products)}")
        
        # Preview table
        st.subheader("Product Preview")
        preview_data = []
        for i, p in enumerate(products[:50], 1):
            preview_data.append({
                '#': i,
                'Product Name': p['product_name'][:60] + '...' if len(p['product_name']) > 60 else p['product_name'],
                'Date': p['acquisition_date'].strftime('%Y-%m-%d') if p['acquisition_date'] else 'N/A',
                'Size (MB)': p['size_mb'],
                'Online': '✅' if p['online'] else '❌'
            })
        
        st.dataframe(preview_data, use_container_width=True, height=400)
        
        if len(products) > 50:
            st.info(f"Showing first 50 of {len(products)} products. Download full list below.")
        
        st.markdown("---")
        
        # Download options
        st.subheader("📥 Download Product List")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Format: /eodata/ Paths Only**")
            st.caption("One path per line (compact format)")
            
            # Generate paths-only content
            paths_content = "\n".join([p['s3_path'] for p in products if p.get('s3_path')])
            
            st.download_button(
                label="📄 Download Paths (.txt)",
                data=paths_content,
                file_name=f"{config.get('product', 'products').replace(' ', '_')}_eodata_paths.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col2:
            st.markdown("**Format: Detailed Information**")
            st.caption("Includes name, date, size, and path")
            
            # Generate detailed content
            detailed_lines = []
            for i, p in enumerate(products, 1):
                date_str = p['acquisition_date'].strftime('%Y-%m-%d %H:%M:%S') if p['acquisition_date'] else 'N/A'
                detailed_lines.append(f"{i}. {p['product_name']}")
                detailed_lines.append(f"   Date: {date_str}")
                detailed_lines.append(f"   Size: {p['size_mb']} MB")
                if p.get('s3_path'):
                    detailed_lines.append(f"   Path: {p['s3_path']}")
                detailed_lines.append("")
            
            detailed_content = "\n".join(detailed_lines)
            
            st.download_button(
                label="📄 Download Detailed (.txt)",
                data=detailed_content,
                file_name=f"{config.get('product', 'products').replace(' ', '_')}_detailed.txt",
                mime="text/plain",
                use_container_width=True
            )
        
    else:
        st.info("No results yet. Execute a query in the 'Query' tab to see results here.")

with tab3:
    st.header("API Information")
    
    st.markdown("""
    ### About This Tool
    
    This interactive web UI provides a user-friendly interface for querying the 
    **Copernicus Data Space Catalogue OData API**.
    
    ### Features
    - 🔍 Interactive product search
    - 🗺️ Spatial filtering (bounding box)
    - 📅 Temporal filtering (date range)
    - 🎯 Tile-specific queries (Sentinel-2)
    - 📥 Download product lists in multiple formats
    - 🛰️ Support for multiple Sentinel missions
    
    ### OData API Endpoint
    ```
    https://catalogue.dataspace.copernicus.eu/odata/v1/Products
    ```
    
    ### Supported Products
    """)
    
    for key, config in PRODUCT_CONFIGS.items():
        with st.expander(f"**{config['name']}** - {config['description']}"):
            st.markdown(f"""
            - **Collection**: {config['collection']}
            - **Product Type**: {config['product_type']}
            - **Instrument**: {config['instrument']}
            - **Requires Tile**: {'Yes' if config['requires_tile'] else 'No'}
            """)
    
    st.markdown("""
    ### Output Formats
    
    #### /eodata/ Paths Only
    Simple list of file paths, one per line:
    ```
    /eodata/Sentinel-2/MSI/L2A_N0500/2017/09/01/S2A_MSIL2A_20170901T101021_N0500_R022_T32TPS_20230929T175520.SAFE
    /eodata/Sentinel-2/MSI/L2A_N0500/2017/09/04/S2A_MSIL2A_20170904T102021_N0500_R065_T32TPS_20230930T014048.SAFE
    ...
    ```
    
    #### Detailed Format
    Includes product metadata:
    ```
    1. S2A_MSIL2A_20170901T101021_N0500_R022_T32TPS_20230929T175520.SAFE
       Date: 2017-09-01 10:10:21
       Size: 850.01 MB
       Path: /eodata/Sentinel-2/MSI/L2A_N0500/2017/09/01/S2A_MSIL2A_20170901T101021_N0500_R022_T32TPS_20230929T175520.SAFE
    ...
    ```
    
    ### How to Use
    1. Select your **Product Type** in the sidebar
    2. Configure **Spatial Extent** (or use preset)
    3. Set **Temporal Extent** (start and end dates)
    4. For Sentinel-2, specify **Tile ID**
    5. Click **Execute Query** button
    6. View results in **Results** tab
    7. Download product list in your preferred format
    
    ### Need Help?
    - [Copernicus Data Space Documentation](https://documentation.dataspace.copernicus.eu/)
    - [OData API Guide](https://documentation.dataspace.copernicus.eu/APIs/OData.html)
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "🛰️ Copernicus Data Space Product Query Tool | "
    "Powered by Streamlit"
    "</div>",
    unsafe_allow_html=True
)
