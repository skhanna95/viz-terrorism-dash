# Import libraries
#####################################################################################################################################################
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from django.conf.urls import include, url
from dash.dependencies import Input, Output
import json
import dash_daq as daq
import locale
import numpy as np

# set locale
#####################################################################################################################################################
locale.setlocale(locale.LC_ALL, '')
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


# data section
####################################################################################################################################################
df_terror = pd.read_csv('terrorism_final.csv')
df_terror = df_terror[(df_terror['Killed'] > 0) | (df_terror['Wounded'] > 0)]
####################################################################################################################################################
def update_country(df):
	df_Terror_By_Country = df[['Region','Country','Code','EventId']]
	df_Terror_By_Country = df_Terror_By_Country.groupby(['Region','Country','Code']).count()
	df_Terror_By_Country = df_Terror_By_Country.reset_index()
	df_Terror_By_Country= df_Terror_By_Country.rename(columns={'EventId':'Count'})
	df_Terror_By_Country['LogCount'] = np.log(df_Terror_By_Country['Count'])
	return df_Terror_By_Country

df_Terror_By_Country = update_country(df_terror)
#---------------------------------------------------------------------------

def update_groups(df):
	df_Groups_By_Country = df[['Group','EventId']]
	df_Groups_By_Country = df_Groups_By_Country.groupby(['Group']).count()
	df_Groups_By_Country = df_Groups_By_Country.reset_index()
	df_Groups_By_Country= df_Groups_By_Country.rename(columns={'EventId':'Count'})
	df_Groups_By_Country = df_Groups_By_Country.sort_values('Count',ascending = False).head(30)
	# group_list = df_Groups_By_Country['Group'].tolist()
	# count_list = df_Groups_By_Country['Count'].tolist()
	# return [group_list,count_list]
	return df_Groups_By_Country

df_Groups_By_Country = update_groups(df_terror)
#-------------------------------------------------------------------------------

def update_attack_type(df):
	df_attack_type = df[['AttackType','EventId']]
	df_attack_type = df_attack_type.groupby(['AttackType']).count()
	df_attack_type = df_attack_type.reset_index()
	df_attack_type= df_attack_type.rename(columns={'EventId':'Count'})
	attack_type_list = df_attack_type['AttackType'].tolist()
	count_list = df_attack_type['Count'].tolist()
	return [attack_type_list,count_list]	

pie_data = update_attack_type(df_terror)[0]
pie_count = update_attack_type(df_terror)[1]


def get_list(a_list,year_range,country,group):
	b=[]
	for i in a_list:
		b.append('Year_Range:'+ str(year_range) + ' | ' + 'Country:'+ str(country) + ' | ' + 'Group:'+ str(group))
	return b

# ------------------------------------------------------------------------------

def update_casualties(df):
	df_casualties = df[['City','Killed','Wounded']]
	df_casualties = df_casualties.groupby(['City']).sum()
	df_casualties = df_casualties.reset_index()
	df_casualties = df_casualties.sort_values('Killed',ascending = False).head(50)
	return df_casualties

df_casualties = update_casualties(df_terror)
city_list = df_casualties['City'].tolist()
killed_list = df_casualties['Killed'].tolist()
wounded_list = df_casualties['Wounded'].tolist()


# Create Empty Dataframe
# --------------------------------------------------------------------------------
df_control = pd.DataFrame(columns=('filter', 'value1','value2'))
df_control = df_control.append([{'filter':'Year','value1':'2000','value2':'2017'}], ignore_index=True)
df_control = df_control.append([{'filter':'Country','value1':'All'}], ignore_index=True)
df_control = df_control.append([{'filter':'Group','value1':'All'}], ignore_index=True)
df_control = df_control.append([{'filter':'AttackType','value1':'All'}], ignore_index=True)
df_control = df_control.append([{'filter':'City','value1':'All'}], ignore_index=True)

# Data Table
#----------------------------------------------------------------------------------
df_table = df_terror[['EventId','Year','Month','Day','Country','City','Group','AttackType','Killed','Wounded','Summary']].head(20)

# Data Summary
#----------------------------------------------------------------------------------
df_summary = df_terror[['Summary']].head(10)

# ----------------------

# Headlines Data -------------------------------------------------------------------
df_headline1 = df_terror[['Year','Killed']]
df_headline1 = df_headline1.groupby(['Year']).sum()
df_headline1 = df_headline1.reset_index()
df_headline1 = df_headline1.astype({'Killed': 'int32'})
total_killed= str(df_headline1['Killed'].sum())
#################################################
df_headline2 = df_terror[['Year','Wounded']]
df_headline2 = df_headline2.groupby(['Year']).sum()
df_headline2 = df_headline2.reset_index()
df_headline2 = df_headline2.astype({'Wounded': 'int32'})
total_wounded= str(df_headline2['Wounded'].sum())
#################################################
df_casualty = df_terror[['Year','Casualties']]
df_casualty = df_casualty.groupby(['Year']).sum()
df_casualty = df_casualty.reset_index()
df_casualty = df_casualty.astype({'Casualties': 'int32'})
avg_yearly_casualty = str((df_casualty['Casualties'].sum())//18)
################################################
group_influence = df_terror[['EventId','Year','Group']]
group_influence = group_influence.groupby(['Year','Group']).count()
group_influence = group_influence.reset_index()
group_influence= group_influence.rename(columns={'EventId':'Count'})

top1_group_influence = group_influence.sort_values('Count',ascending = False).head(1) 
most_influential_group = top1_group_influence.values[0][1]
import os
# body
####################################################################################################################################################
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server=app.server
server.secret_key = os.environ.get('secret_key', 'secret')

styles = {
	'pre': {
		'border': 'thin lightgrey solid',
		'overflowX': 'scroll'
	}
}

#---------------------------------------------------------------------------------------------------------------------------------------------------
app.layout = html.Div(style={'backgroundColor':'white'},children=[ 

	# Main Header
	# **********************************************************************************************************************************************
	html.Div(className="app-header",
			 children=[ html.Div('Global Terrorism Activity (2000-2017)', className="app-header--title") ]
			),

	# Year Range Slider
	# **********************************************************************************************************************************************
	# dcc.Markdown('''** Select Year Range (00 -> Year 2000 **): ''', className="year_range_slider"),

	# html.Div(className="year_range_slider",
	# 	children=[ html.Div('Select Year Range (00 -> Year 2000)', 'Killed',
	# 		style={'display': 'inline-block'},	
	# 		),
		  
	# ]),

	html.Div([ 
		html.Div('Select Year Range (From Year 2000 to 2017)', 
		style={'display': 'inline'},
		className="year_range_slider"),

		html.Div('Killed', 
		style={'display': 'inline'},
		className="h1_text"),

		html.Div('Wounded', 
		style={'display': 'inline'},
		className="h2_text"),

		html.Div('Avg Yearly Casualty', 
		style={'display': 'inline'},
		className="h3_text"),

		html.Div('Most Influential Group', 
		style={'display': 'inline'},
		className="h4_text"),


		],
	),

	##################################################################

	#html.Div('',style={'display': 'block'}),

	##################################################################


	html.Div(
		className="year_filter",
		children = [
	html.Div([
		dcc.RangeSlider(
			id='range-slider1',
			min=df_terror['Year'].min(),
			max=df_terror['Year'].max(),
			step=1,
			value=[df_terror['Year'].min(), df_terror['Year'].max()],
			marks={2000:'00', 2001:'01', 2002:'02', 2003:'03', 2004:'04',2005:'05', 2006:'06', 2007:'07', 2008:'08', 2009:'09',2010:'10',
			2011:'11', 2012:'12', 2013:'13', 2014:'14', 2015:'15',2016:'16', 2017:'17'
			},
		),
		html.Div(id='output-container-range-slider'),
	]),
	], style={'width': '30%', 'display': 'inline-block'}),
	#-----------------------------------------------------------------


	# Adding Link to Forced Layout
	# html.A(html.Button('Submit feedback!', className='three_columns'),
 #    href='https://localhost:63342/Forced Layout/?_ijt=d8ftgh3oauaeho3bplgmd9pnso'),


 	# Adding Data Tables Side By Side
	html.Div([
	 	dcc.Textarea(
	 	id = 'textarea1',
	    placeholder='Total Killed',
	    value=total_killed,
	    style={'fontWeight':'bold', 'textAlign':'center', 'font-size':'15px','padding-top':'20px', 'color':'darkred','font-family':'arial'},
	    #disabled = True
	    readOnly = True
		)],
		style={'display': 'inline-block'}, className="textbox1"
	),

	html.Div([
	 	dcc.Textarea(
	 	id = 'textarea2',
	    placeholder='Total Wounded',
	    value=total_wounded,
	    style={'fontWeight':'bold', 'textAlign':'center', 'font-size':'15px','padding-top':'20px', 'color':'darkred', 'height':'20px'},
	    readOnly = True
		)],
		style={'display': 'inline-block'}, className="textbox2"
	),


	html.Div([
	 	dcc.Textarea(
	 	id = 'textarea3',
	    placeholder='Average Casualty',
	    value=avg_yearly_casualty,
	    style={'fontWeight':'bold', 'textAlign':'center', 'font-size':'15px','padding-top':'20px', 'color':'darkred', 'height':'20px'},
	    readOnly = True,
		)],
		style={'display': 'inline-block'}, className="textbox3"
	),

	html.Div([
	 	dcc.Textarea(
	 	id = 'textarea4',
	    placeholder='Most Influential Group',
	    value=most_influential_group,
	    style={'fontWeight':'bold', 'textAlign':'center', 'font-size':'15px','padding-top':'20px', 'color':'darkred', 'height':'20px'},
	    readOnly = True,
		)],
		style={'display': 'inline-block'}, className="textbox4"
	),



	# html.Div([
	# 	html.Button('D3 Viz', id='button_d3'),
	# ], style={'display': 'inline', 'width':'100px', 'padding-top':'200px'}, className="button1"),

	# html.Div([
	# 	html.Button('D3 Viz', id='button_d3'),
	# ], style={'display': 'inline'}, className="button1"),

	# # Adding Arrow image
	# html.Div(
	# 	html.Img(src=app.get_asset_url('arrow11.png')),
	# 	style={'display': 'inline-block'}, className="arrow1"),

	##################################################################

	html.Div('',style={'display': 'block'}),

	##################################################################

#html.Div([ 


	# Adding Arrow image
	html.Div([
		html.Img(src=app.get_asset_url('arrow12.png'), style={'display': 'inline'}, className="arrow1",),
		#style={'display': 'block'}, className="arrow1",

		# html.Div('You have selected Year_Range ' + '[' + str(df_control.loc[0][1]) + '-' + str(df_control.loc[0][2]) + '].' + ' Now hover over and select a country on the map below to drill down.', 
		# style={'display': 'inline'},
		# className="arrow1_text"),

		html.Div(
	 	dcc.Textarea(
	 	id = 'textarea5',
	    placeholder='Year Range',
	    value='Year Range Selected: [2000-2017]',
	    style={'fontWeight':'bold', 'textAlign':'center', 'font-size':'15px','padding-top':'15px', 'color':'darkred', 'height':'10px','margin-left':'10px'},
	    readOnly = True,
		),
		style={'display': 'inline-block'}, className="textbox5"),

		]),


	##################################################################

	# Map - graph 1
	# **********************************************************************************************************************************************
	
	#################

	html.Div([
		html.H5(''),
		dcc.Graph(
			id='g1',
			figure=(px.choropleth(df_Terror_By_Country, locations="Code", color="Count", hover_name="Country", range_color=[df_Terror_By_Country['Count'].min(),df_Terror_By_Country['Count'].max()],projection="natural earth",color_continuous_scale=px.colors.sequential.Reds, height=500)).update_layout(margin=dict(l=0, r=0, t=25, b=5),title_text='Terrorism Count By Country'),
			# figure=px.scatter_geo(df_Terror_By_Country, locations="Code",hover_name="Country", size="Count", projection="natural earth"),
			config={
					'displayModeBar': False
					},       
				)
	], style={'display': 'inline-block'}, className="class_g1"),     
	#-----------------------------------------------------------------


	# Adding Arrow image
	html.Div([
		html.Img(src=app.get_asset_url('arrow20.png'),style={'display': 'inline'}, className="arrow2"),
		
		html.Div(
	 	dcc.Textarea(
	 	id = 'textarea6',
	    placeholder='Country',
	    value='Country Selected: All',
	    style={'fontWeight':'bold', 'textAlign':'center', 'font-size':'15px','padding-top':'15px', 'color':'darkred', 'height':'10px', 'margin-left':'10px'},
	    readOnly = True,
		),
		style={'display': 'inline'}, className="textbox6"),

		html.Div(
	 	dcc.Textarea(
	 	id = 'textarea7',
	    placeholder='Group',
	    value='Group Selected: All',
	    style={'fontWeight':'bold', 'textAlign':'center', 'font-size':'15px','padding-top':'15px', 'color':'darkred', 'height':'10px', 'margin-left':'430px'},
	    readOnly = True,
		),
		style={'display': 'inline'}, className="textbox7"),

		]),

	# Barchart - graph 2
	# ************************************************************
	html.Div([
		html.H5(''),
		dcc.Graph(
			id='g2',
			# figure={
			# 		'data': [ { 'x': df_Groups_By_Country['Group'],'y': df_Groups_By_Country['Count'],  'type': 'bar', 'name': 'Terrorism', 
			# 		'marker': {'color': ['darkred','maroon','firebrick','crimson','red','indianred','orangered','tomato','lightcoral','salmon',
			# 							 'darksalmon','lightsalmon', 'burlywood', 'cadetblue','chartreuse', 'chocolate', 'coral', 'cornflowerblue','cornsilk', 
			# 							 'crimson', 'cyan', 'darkblue', 'darkcyan','darkgoldenrod', 'darkgray', 'darkgrey', 'darkgreen','darkkhaki', 
			# 							 'darkmagenta', 'darkolivegreen']}}],
			# 		'layout': {'title': 'Terrorism Count By Group'},
			# 		},

			figure = (px.bar(df_Groups_By_Country, x='Group', y='Count',
			hover_data=['Group', 'Count'], color='Group',height=500,
			color_discrete_sequence=['darkred','firebrick','crimson','red','indianred','orangered','tomato','lightcoral','salmon','darksalmon','lightsalmon'])).update_layout(showlegend=False,margin=dict(l=0, r=0, t=25, b=20), title_text='Terrorism Count By Group',
			xaxis=dict(
	        autorange=True,
	        showgrid=False,
	        ticks='',
	        showticklabels=False
    )),

			config={
					'displayModeBar': False
					},
				),
		html.Pre(id='click-data'),
	], style={'display': 'inline-block'}, className="class_g2"),

	#-----------------------------------------------------------------

	# Adding Arrow image
	html.Div(
		html.Img(src=app.get_asset_url('arrow30.png')),
		style={'display': 'inline-block','vertical-align': 'middle'}, className="arrow3"),

	# Pie - graph 3
	# ************************************************************
	html.Div([
		html.H5(style={"textAlign": "center"}),
		dcc.Graph(
			id='g3',
			figure=(go.Figure(
				data=[go.Pie(labels=pie_data,
							values=pie_count,
							hole=0.6)],
							layout=go.Layout(
							title='Terrorism Count By Attack Type', colorway= ['darkred','firebrick','crimson','red','indianred','orangered','tomato','lightcoral','salmon',
										 'darksalmon','lightsalmon'])
							)).update_layout(showlegend=False,margin=dict(l=0, r=0, t=45, b=20)),
			config={
					'displayModeBar': False
					},       
				)
	], style={'display': 'inline-block'}, className="class_g3"),     



	# Adding Arrow image ----------------------------------------------
	html.Div([
			html.Img(src=app.get_asset_url('arrow40.png'),style={'display': 'inline','vertical-align': 'center'}, className="arrow4",),
			
		html.Div(
		 	dcc.Textarea(
		 	id = 'textarea8',
		    placeholder='AttackType',
		    value='Attack Type Selected: All',
		    style={'fontWeight':'bold', 'textAlign':'center', 'font-size':'15px','padding-top':'15px', 'color':'darkred', 'margin-left':'10px'},
		    readOnly = True,
			),
			style={'display': 'inline'}, className="textbox8"),
		]),

	# html.Div([

	# 	html.Div(
	# 	html.Img(src=app.get_asset_url('arrow40.png'),
	# 		style={'display': 'inline'}, className="arrow4"),
	# 	),
		
	# 	html.Div(
	#  	dcc.Textarea(
	#  	id = 'textarea8',
	#     placeholder='AttackType',
	#     value='Attack Type Selected: All',
	#     style={'fontWeight':'bold', 'textAlign':'center', 'font-size':'15px','padding-top':'15px', 'color':'darkred', 'height':'10px', 'margin-left':'1200px'},
	#     readOnly = True,
	# 	),
	# 	style={'display': 'inline'}, className="textbox8"),



	# 	]),

	# Barchart - graph 4
	# ************************************************************
	html.Div([
		html.H5(''),
		dcc.Graph(
			id='g4',
			figure=(go.Figure(data=[
							go.Bar(name='Killed', x=city_list, y=killed_list),
							go.Bar(name='Wounded', x=city_list, y=wounded_list)
								  ],
			layout=go.Layout(
					title='Casualties',
					showlegend=True,
					barmode='stack',
					colorway=['black','darkred']
							))).update_layout(margin=dict(l=20, r=0, t=25, b=35),xaxis_tickangle=-45),
			config={
					'displayModeBar': False
					},
				),
		html.Pre(id='click-data1'),
	], style={'display': 'inline-block'}, className="class_g4"),


	# Adding Arrow image ----------------------------------------------
	# html.Div(
	# 	html.Img(src=app.get_asset_url('arrow50.png')),
	# 	style={'display': 'block'}, className="arrow5"),

	html.Div([
		html.Img(src=app.get_asset_url('arrow50.png'),style={'display': 'inline','vertical-align': 'center'}, className="arrow5",),
			
		html.Div(
		 	dcc.Textarea(
		 	id = 'textarea9',
		    placeholder='City',
		    value='City Selected: All',
		    style={'fontWeight':'bold', 'textAlign':'center', 'font-size':'15px','padding-top':'15px', 'color':'darkred', 'margin-left':'10px'},
		    readOnly = True,
			),
			style={'display': 'inline'}, className="textbox9"),
		]),



	# Data Table
	# ###########################################################################
	html.Div([

	dash_table.DataTable(
	id = 'data_table1',
	data=df_table.to_dict('records'),
	columns=[{'id': c, 'name': c} for c in df_table.columns],
	fixed_rows={ 'headers': True, 'data': 0 },
	style_cell={'width': '100px'},
	style_header={'backgroundColor': 'white','fontWeight': 'bold'},
	style_data={'whiteSpace': 'normal','height': 'auto'},
	style_cell_conditional=[
	{'if': {'column_id': 'EventId'},'width': '50px'},
	{'if': {'column_id': 'Year'},'width': '40px'},
	{'if': {'column_id': 'Month'},'width': '40px'},
	{'if': {'column_id': 'Day'},'width': '40px'},
	{'if': {'column_id': 'Killed'},'width': '40px'},
	{'if': {'column_id': 'Wounded'},'width': '45px'},
	{'if': {'column_id': 'AttackType'},'width': '50px'},
	{'if': {'column_id': 'Summary'},'width': '500px'},
	],
	) ,
	], style={'display': 'inline-block'}, className="class_g5"),

	#--------------------------------------------------------------


	# Filters --------------------------------------------------------

	html.Div([

		dash_table.DataTable(
		id = 'data_table0',
		data=df_control.to_dict('records'),
		columns=[{'id': c, 'name': c} for c in df_control.columns],
		fixed_rows={ 'headers': True, 'data': 0 },
		style_cell={'width': 'auto'},
		style_header={'backgroundColor': 'white','fontWeight': 'bold'},
		style_data={'whiteSpace': 'normal','height': 'auto'},
		) ,
		], style={'display': 'inline-block'}, className="class_g0"),



])
#---------------------------------------------------------------------------------------------------------------------------------------------------



app.css.append_css({
	'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})  


#callback section
####################################################################################################################################################

# Update Text Area 1
@app.callback(Output('textarea1','value'),
			  [Input('range-slider1', 'value')])

def update_data_table_h1(selected_year_range):	

	if ((selected_year_range[0]==2000) & (selected_year_range[1]==2017)):
		data_value = str(format(df_headline1['Killed'].sum(),',d'))

	else:
		year_min = str(selected_year_range[0])
		year_max = str(selected_year_range[1])

		df_h1 = df_headline1[(df_headline1['Year'] >= selected_year_range[0]) & (df_headline1['Year'] <= selected_year_range[1])]

		data_value = str(format(df_h1['Killed'].sum(),',d'))

	return data_value

##############################################################################################
# Update Text Area 2
@app.callback(Output('textarea2','value'),
			  [Input('range-slider1', 'value')])

def update_data_table_h2(selected_year_range):	

	if ((selected_year_range[0]==2000) & (selected_year_range[1]==2017)):
		data_value = str(format(df_headline2['Wounded'].sum(),',d'))

	else:
		year_min = str(selected_year_range[0])
		year_max = str(selected_year_range[1])

		df_h2 = df_headline2[(df_headline2['Year'] >= selected_year_range[0]) & (df_headline2['Year'] <= selected_year_range[1])]
		data_value = str(format(df_h2['Wounded'].sum(),',d'))

	return data_value

##############################################################################################
# Update Text Area 3
@app.callback(Output('textarea3','value'),
			  [Input('range-slider1', 'value')])

def update_data_table_h3(selected_year_range):	

	if ((selected_year_range[0]==2000) & (selected_year_range[1]==2017)):
		data_value = str(format((df_casualty['Casualties'].sum())//18,',d'))

	else:
		year_min = str(selected_year_range[0])
		year_max = str(selected_year_range[1])
		years = selected_year_range[1] - selected_year_range[0] + 1

		df_h3 = df_casualty[(df_casualty['Year'] >= selected_year_range[0]) & (df_casualty['Year'] <= selected_year_range[1])]
		data_value = str(format((df_h3['Casualties'].sum())//years,',d'))

	return data_value

##############################################################################################
# Update Text Area 4
@app.callback(Output('textarea4','value'),
			  [Input('range-slider1', 'value')])

def update_data_table_h4(selected_year_range):	

	if ((selected_year_range[0]==2000) & (selected_year_range[1]==2017)):

		df1 = group_influence.sort_values('Count',ascending = False).head(1) 
		data_value = df1.values[0][1] + ' (' +  str(df1.values[0][2]) + ')' 

	else:
		year_min = str(selected_year_range[0])
		year_max = str(selected_year_range[1])

		df_h4 = group_influence[(group_influence['Year'] >= selected_year_range[0]) & (group_influence['Year'] <= selected_year_range[1])]
		
		top1_group_influence = df_h4.sort_values('Count',ascending = False).head(1) 
		data_value = top1_group_influence.values[0][1] + ' (' +  str(top1_group_influence.values[0][2]) + ')' 

	return data_value


##############################################################################################
# Update Text Area 5
@app.callback(Output('textarea5','value'),
			  [Input('range-slider1', 'value')])

def update_data_table_h5(selected_year_range):	

	if ((selected_year_range[0]==2000) & (selected_year_range[1]==2017)):


		data_value = 'Year Range Selected: [2000-2017]'

	else:
		year_min = str(selected_year_range[0])
		year_max = str(selected_year_range[1])

		data_value = 'Year Range Selected: ' + '[' + year_min + '-' + year_max + ']'

	return data_value

##############################################################################################
# Update Text Area 6
@app.callback(Output('textarea6','value'),
			 [Input('g1', 'clickData')])

def update_data_table_h6(clickData):	

	if isinstance(clickData, type(None)):
		data_value = 'Country Selected: All'

	else:
		country = str(clickData['points'][0]['hovertext'])

		data_value = 'Country Selected: ' + country

	return data_value


##############################################################################################
# Update Text Area 7
@app.callback(Output('textarea7','value'),
			 [Input('g2', 'clickData')])

def update_data_table_h7(clickData):	

	if isinstance(clickData, type(None)):
		data_value = 'Group Selected: All'

	else:
		group = str(clickData['points'][0]['x'])
		data_value = 'Group Selected: ' + group

	return data_value

##############################################################################################
# Update Text Area 8
@app.callback(Output('textarea8','value'),
			 [Input('g3', 'clickData')])

def update_data_table_h8(clickData):	

	if isinstance(clickData, type(None)):
		data_value = 'Attack Type Selected: All'

	else:
		attack_type = str(clickData['points'][0]['label'])
		data_value = 'Attack Type Selected: ' + attack_type

	return data_value


##############################################################################################
# Update Text Area 9
@app.callback(Output('textarea9','value'),
			 [Input('g4', 'clickData')])

def update_data_table_h9(clickData):	

	if isinstance(clickData, type(None)):
		data_value = 'City Selected: All'

	else:
		city =  str(clickData['points'][0]['x'])
		data_value = 'City Selected: ' + city

	return data_value

# Update Data Table H1
#######################################################################
# @app.callback([Output('data_table_h1','data')],
# 			  [Input('range-slider1', 'value')])

# def update_data_table_h1(selected_year_range):	

# 	if ((selected_year_range[0]==2000) & (selected_year_range[1]==2017)):

# 		data_list = list(df_headline1['Killed'].sum())
  
# 		# Create the pandas DataFrame 
# 		df = pd.DataFrame(data_list, columns = ['Killed']) 
# 		data1 = df.to_dict('records')				
# 	else:
# 		year_min = str(selected_year_range[0])
# 		year_max = str(selected_year_range[1])

# 		df_h1 = df_headline1[(df_headline1['Year'] >= selected_year_range[0]) & (df_headline1['Year'] <= selected_year_range[1])]
# 		df_h1_list = list(df_h1['Killed'].sum())
# 		df = pd.DataFrame(df_h1_list, columns = ['Killed']) 
# 		data1 = df.to_dict('records')

# 	return  data1


# Callback for Pie Chart
#update_pie_year(df_terror[df_terror['Year']==clickData['points'][0]['x']])[0]
#######################################################################
@app.callback(Output('g3','figure'),
			  [Input('g2', 'clickData')])

def update_pie_chart(clickData):

	print(clickData)

	if isinstance(clickData, type(None)):
		figure = (go.Figure(
					data=[go.Pie(labels=pie_data,
								values= pie_count,
								textinfo='none',
								#text= get_list(pie_data,'2000-2017','All','All'),
								#hovertemplate = "%{label}: <br>Popularity: %{percent} </br> %{text}",
								hole =0.6,
								marker={'line.width':3, 'line.color':'white'}
								)],
								layout=go.Layout(
								title='Terrorism Count By AttackType', colorway= ['darkred','darkblue','darkgreen','darkorange','darkslategray','crimson','darkslateblue','slategray','olive',
								'slateblue','chocolate','dimgray','firebrick'])
						)).update_layout(showlegend=False,margin=dict(l=0, r=0, t=45, b=40),annotations=[dict(text='Year_Range:2000-2017' + ' <br />  ' + 'Country:All' + ' <br />  ' + 'Group:All', x=0, y=-0.1, font_size=12, showarrow=False)])       
				
	else:

		df_control.loc[2][1] = str(clickData['points'][0]['x'])

		print(df_control)

		year_min = int(df_control.loc[0][1])
		year_max = int(df_control.loc[0][2])		
		country = df_control.loc[1][1]

		filtered_df = df_terror[(df_terror['Year'] >= year_min) & (df_terror['Year'] <= year_max)]
		filtered_df = filtered_df[(filtered_df['Country'] == country)]

		# pie_data = update_groups(df_terror[(df_terror['Country'] == clickData['points'][0]['hovertext'])])[0]
		# pie_count = update_groups(df_terror[(df_terror['Country'] == clickData['points'][0]['hovertext'])])[1]

		figure = (go.Figure(
					data=[go.Pie(labels=filtered_df[filtered_df['Group']==clickData['points'][0]['x']][['AttackType','EventId']].groupby(['AttackType']).count().reset_index().rename(columns={'EventId':'Count'})['AttackType'].tolist(),
								values=filtered_df[filtered_df['Group']==clickData['points'][0]['x']][['AttackType','EventId']].groupby(['AttackType']).count().reset_index().rename(columns={'EventId':'Count'})['Count'].tolist(),
								textinfo='none',
								#text= get_list(filtered_df[filtered_df['Group']==clickData['points'][0]['x']][['AttackType','EventId']].groupby(['AttackType']).count().reset_index().rename(columns={'EventId':'Count'})['AttackType'].tolist(),str(year_min)+'-' + str(year_max),country,str(clickData['points'][0]['x'])),
								#hovertemplate = "%{label}: <br>Popularity: %{percent} </br> %{text}",
								hole=0.6,
								marker={'line.width':3, 'line.color':'white'}
								)],
								layout=go.Layout(
								title='Terrorism Count By AttackType', colorway= ['darkred','darkblue','darkgreen','darkorange','darkslategray','crimson','darkslateblue','slategray','olive',
								'slateblue','chocolate','dimgray','firebrick'])
						)).update_layout(showlegend=False, margin=dict(l=0, r=0, t=45, b=40),annotations=[dict(text='Year_Range:'+ str(year_min)+'-' + str(year_max) + ' <br />  ' + 'Country:'+ country +' <br />  ' + 'Group:' + str(clickData['points'][0]['x']), x=0, y=-0.1, font_size=12, showarrow=False)])      
				
	return figure

######################################################################################################################################################

# Callback for year slider
@app.callback(
	[Output('g1', 'figure')],
	[Input('range-slider1', 'value')]
			)

def update_fig1(selected_year_range):

	print(selected_year_range)

	if ((selected_year_range[0]==2000) & (selected_year_range[1]==2017)):
		df_Terror_By_Country['Year_Range'] = '[2000-2017]'

		figure1 = (px.choropleth(df_Terror_By_Country, locations="Code", color="Count", hover_name="Country",hover_data=['Year_Range'], range_color=[df_Terror_By_Country['Count'].min(),df_Terror_By_Country['Count'].max()],projection="natural earth",color_continuous_scale=px.colors.sequential.Reds,height=500)).update_layout(margin=dict(l=0, r=0, t=25, b=5),title_text='Terrorism Count By Country'),
		# figure1 = px.scatter_geo(df_Terror_By_Country, locations="Code",hover_name="Country", size="Count", projection="natural earth")

	else:

		# update selected Year Range in database 
		df_control.loc[0][1] = str(selected_year_range[0])
		df_control.loc[0][2] = str(selected_year_range[1])
		print(df_control)

		filtered_df1 = df_terror[(df_terror['Year'] >= selected_year_range[0]) & (df_terror['Year'] <= selected_year_range[1])]
		filtered_df1 = update_country(filtered_df1)
		filtered_df1['Year_Range'] = '[' + str(selected_year_range[0]) + '-' + str(selected_year_range[1]) + ']'


		figure1 = (px.choropleth(filtered_df1, locations="Code", color="Count", hover_name="Country",hover_data=["Year_Range"], range_color=[filtered_df1['Count'].min(),filtered_df1['Count'].max()],projection="natural earth",color_continuous_scale=px.colors.sequential.Reds,height=500)).update_layout(margin=dict(l=0, r=0, t=25, b=5),title_text='Terrorism Count By Country'),

		# figure1 = px.scatter_geo(filtered_df1, locations="Code",hover_name="Country", size="Count", projection="natural earth")


	return figure1



# Callback for Pie Chart
#update_pie_year(df_terror[df_terror['Year']==clickData['points'][0]['x']])[0]
#######################################################################
@app.callback(Output('g2','figure'),
			  [Input('g1', 'clickData')])

def update_bar_chart(clickData):	

	if isinstance(clickData, type(None)):
		# figure={
		# 		'data': [ { 'x': df_Groups_By_Country['Group'],'y': df_Groups_By_Country['Count'],  'type': 'bar', 'name': 'Terrorism',
		# 		'marker': {'color': ['darkred','maroon','firebrick','crimson','red','indianred','orangered','tomato','lightcoral','salmon',
		# 							 'darksalmon','lightsalmon', 'burlywood', 'cadetblue','chartreuse', 'chocolate', 'coral', 'cornflowerblue','cornsilk', 
		# 							 'crimson', 'cyan', 'darkblue', 'darkcyan','darkgoldenrod', 'darkgray', 'darkgrey', 'darkgreen','darkkhaki', 
		# 							 'darkmagenta', 'darkolivegreen']}} ],
		# 		'layout': {'title': 'Terrorism Count By Group'}
		# 	   } 

		df_control.loc[0][1] = str(2000)
		df_control.loc[0][2] = str(2017)
		data = df_control.to_dict('records')

		df_Groups_By_Country['Year_Range'] = '[2000-2017]'
		df_Groups_By_Country['Country'] = df_control.loc[1][1]

		figure = (px.bar(df_Groups_By_Country, x='Group', y='Count',
		hover_data=['Year_Range','Country','Group', 'Count'], color='Group', height=500,
		color_discrete_sequence=['darkred','darkblue','darkgreen','darkorange','indigo','darkslategray','crimson','darkslateblue','slategray','red',
								'slateblue','indianred','dimgray','green','orangered','gray','tomato', 'darkgray','olivedrab', 'teal',
								'salmon', 'darkblue','darksalmon', 'chocolate','lightsalmon','goldenrod','peru','sienna','brown','olive'])).update_layout(showlegend=False,margin=dict(l=0, r=0, t=25, b=20), title_text='Terrorism Count By Group',
		xaxis=dict(
        autorange=True,
        showgrid=False,
        ticks='',
        showticklabels=False
    ),yaxis={'tickformat': ',d'})




	else:
		# update selected country 
		df_control.loc[1][1] = str(clickData['points'][0]['hovertext'])
		print(df_control)

		#print(clickData['points'][0]['hovertext'])
		# get selected year
		year_min = int(df_control.loc[0][1])
		year_max = int(df_control.loc[0][2])		

		filtered_df = df_terror[(df_terror['Year'] >= year_min) & (df_terror['Year'] <= year_max)]
		filtered_df = filtered_df[(filtered_df['Country'] == clickData['points'][0]['hovertext'])]
		filtered_df = update_groups(filtered_df)
		filtered_df['Year_Range'] = '[' + str(year_min) + '-' + str(year_max) + ']'
		filtered_df['Country'] = df_control.loc[1][1]
		# figure={
		# 		'data': [ { 'x': filtered_df['Group'],'y': filtered_df['Count'],  'type': 'bar', 'name': 'Terrorism',
		# 		'marker': {'color': ['darkred','maroon','firebrick','crimson','red','indianred','orangered','tomato','lightcoral','salmon',
		# 							 'darksalmon','lightsalmon', 'burlywood', 'cadetblue','chartreuse', 'chocolate', 'coral', 'cornflowerblue','cornsilk', 
		# 							 'crimson', 'cyan', 'darkblue', 'darkcyan','darkgoldenrod', 'darkgray', 'darkgrey', 'darkgreen','darkkhaki', 
		# 							 'darkmagenta', 'darkolivegreen']}} ],
		# 		'layout': {'title': 'Terrorism Count By Group'}
		# 		}    

		figure = (px.bar(filtered_df, x='Group', y='Count',
		hover_data=['Year_Range','Country','Group', 'Count'], color='Group', height=500,
		color_discrete_sequence=['darkred','darkblue','darkgreen','darkorange','indigo','darkslategray','crimson','darkslateblue','slategray','red',
								'slateblue','indianred','dimgray','green','orangered','gray','tomato', 'darkgray','olivedrab', 'teal',
								'salmon', 'darkblue','darksalmon', 'chocolate','lightsalmon','goldenrod','peru','sienna','brown','olive'])).update_layout(showlegend=False,margin=dict(l=0, r=0, t=25, b=20), title_text='Terrorism Count By Group',
		xaxis=dict(
        autorange=True,
        showgrid=False,
        ticks='',
        showticklabels=False
    ),yaxis={'tickformat': ',d'})

		data = df_control.to_dict('records') 
	
	return figure

# Update stacked barchart
#######################################################################
@app.callback(Output('g4','figure'),
			  [Input('g3', 'clickData')])

def update_stacked_barchart(clickData):	

	if isinstance(clickData, type(None)):
		figure=(go.Figure(data=[
				go.Bar(name='Killed', x=city_list, y=killed_list),
				go.Bar(name='Wounded', x=city_list, y=wounded_list)
				],
		  layout=go.Layout(
				title='Casualties',
				showlegend=True,
				barmode='stack',
				colorway=['black','red']
		))).update_layout(margin=dict(l=20, r=0, t=25, b=35), yaxis={'tickformat': ',d'}, xaxis_tickangle=-45,annotations=[dict(text='Year_Range:2000-2017' + ' <br /> ' + 'Country:All' + ' <br /> ' + 'Group:All' + ' <br /> ' + 'Attack Type:All', x=50, y=max(killed_list,default=0) + max(wounded_list,default=0), xref='x', yref='y', font_size=12, showarrow=False)])   
				
	else:

		# print(clickData['points'][0]['label'])

		# update selected country 
		df_control.loc[3][1] = str(clickData['points'][0]['label'])
		print(df_control)

		year_min = int(df_control.loc[0][1])
		year_max = int(df_control.loc[0][2])		
		country = df_control.loc[1][1]
		group = df_control.loc[2][1]
		attack_type = df_control.loc[3][1]

		filtered_df = df_terror[(df_terror['Year'] >= year_min) & (df_terror['Year'] <= year_max)]
		filtered_df = filtered_df[filtered_df['Country'] == country]
		filtered_df = filtered_df[filtered_df['Group'] == group]
		filtered_df = filtered_df[filtered_df['AttackType'] == attack_type]

		# filtered_df = update_casualties(df_terror[(df_terror['AttackType'] == clickData['points'][0]['label'])])
		filtered_df = update_casualties(filtered_df)

		city_list1 = filtered_df['City'].tolist()
		killed_list1 = filtered_df['Killed'].tolist()
		wounded_list1 = filtered_df['Wounded'].tolist()

		figure=(go.Figure(data=[
				go.Bar(name='Killed', x=city_list1, y=killed_list1),
				go.Bar(name='Wounded', x=city_list1, y=wounded_list1)
				],
		  layout=go.Layout(
				title='Casualties',
				showlegend=True,
				barmode='stack',
				colorway=['black','red']
		))).update_layout(margin=dict(l=20, r=0, t=25, b=35), yaxis={'tickformat': ',d'},xaxis_tickangle=-45,annotations=[dict(text='Year_Range:'+ str(year_min)+'-' + str(year_max) + ' <br />  ' + 'Country:'+ country +' <br />  ' + 'Group:' + group +' <br />  ' + 'Attack Type:' + attack_type, x=50, y=max(killed_list1,default=0) + max(wounded_list1,default=0), xref='x', yref='y', font_size=12, showarrow=False)])   
	
	return figure

# Update Data Table
#######################################################################
@app.callback([Output('data_table1','data'),Output('data_table0','data')],
			  [Input('g4', 'clickData')])

def update_data_table(clickData):	

	if isinstance(clickData, type(None)):
		data1 = df_table.to_dict('records')

		df_control.loc[0][1] = str(2000)
		df_control.loc[0][2] = str(2017)
		data0 = df_control.to_dict('records')

				
	else:

		# print(clickData)
		print(clickData['points'][0]['x'])

		# update selected city 
		df_control.loc[4][1] = str(clickData['points'][0]['x'])
		# print(df_control)

		year_min = int(df_control.loc[0][1])
		year_max = int(df_control.loc[0][2])		
		country = df_control.loc[1][1]
		group = df_control.loc[2][1]
		attack_type = df_control.loc[3][1]
		city = df_control.loc[4][1]

		filtered_df = df_terror[(df_terror['Year'] >= year_min) & (df_terror['Year'] <= year_max)]
		filtered_df = filtered_df[filtered_df['Country'] == country]
		filtered_df = filtered_df[filtered_df['Group'] == group]
		filtered_df = filtered_df[filtered_df['AttackType'] == attack_type]
		filtered_df = filtered_df[filtered_df['City'] == city]

		data1 = filtered_df.to_dict('records')
		data0 = df_control.to_dict('records')

	return  data1, data0


# main code
####################################################################################################################################################
if __name__ == '__main__':

	app.run_server(debug=True)
