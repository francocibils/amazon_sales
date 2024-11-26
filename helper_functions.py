import pandas as pd

def processing_sales(df, catalog, brand):

    # Rename brand
    brand = 'All ' + brand

    # Amazon dataframe
    # Amazon dataframe
    amazon_df = pd.merge(df, catalog, left_on = 'SKU', right_on = 'SKU (AMAZON)', how = 'left')
    amazon_df['Ventas de productos pedidos'] = amazon_df['Ventas de productos pedidos'].str.replace(r'[^\d.]', '', regex = True).astype(float)
    amazon_df['Ventas de productos pedidos - B2B'] = amazon_df['Ventas de productos pedidos - B2B'].str.replace(r'[^\d.]', '', regex = True).astype(float)
    amazon_df['Revenue'] = amazon_df['Ventas de productos pedidos'] + amazon_df['Ventas de productos pedidos - B2B']
    amazon_df['Quantity'] = amazon_df['Total de artículos del pedido'] + amazon_df['Total de artículos del pedido -B2B']
    amazon_df = amazon_df[['Date', 'FAMILIA DE PRODUCTO', 'Revenue', 'Quantity']]
    amazon_df.columns = ['Date', 'Product family', 'Revenue', 'Quantity']

    # Total
    total_amazon_df = amazon_df.groupby('Date')[['Revenue', 'Quantity']].sum()
    total_amazon_df['Product family'] = 'All Inova'
    total_amazon_df = total_amazon_df.reset_index()

    # Group by date and family product
    amazon_df = amazon_df.groupby(['Date', 'Product family']).sum().reset_index()

    # Concat
    sales_df = pd.concat([amazon_df, total_amazon_df])

    # Define all possible products and channels
    all_days = sales_df['Date'].unique()
    all_products = ['All Inova'] + catalog['FAMILIA DE PRODUCTO'].unique().tolist()

    # Create a MultiIndex DataFrame with all combinations of products and channels
    multi_index = pd.MultiIndex.from_product([all_days, all_products], names = ['Date', 'Product family'])

    # Reindex the original DataFrame to this new index
    df_reindexed = sales_df.set_index(['Date', 'Product family']).reindex(multi_index, fill_value = 0).reset_index()

    # Pivot table
    df_pivot = df_reindexed.pivot_table(index = 'Date', 
                          columns = 'Product family', 
                          values = ['Revenue', 'Quantity'], 
                          aggfunc = 'sum')

    # Flatten the MultiIndex in the columns
    df_pivot.columns = [f'{col[1]} - {col[0]}' for col in df_pivot.columns]

    # Order the columns as 'Product A - Revenue', 'Product A - Quantity'
    sorted_columns = []
    product_families = df_reindexed['Product family'].unique()

    for product in product_families:
        sorted_columns.append(f'{product} - Revenue')
        sorted_columns.append(f'{product} - Quantity')

    # Reorder the columns
    df_pivot = df_pivot[sorted_columns]

    # Reset index to bring 'date' back as a column
    df_pivot = df_pivot.reset_index()
    df_pivot = df_pivot.fillna(0)

    return sales_df, df_pivot