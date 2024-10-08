import matplotlib.pyplot as plt
import csv
from datetime import datetime, timedelta

__author__ = "Devanshi Prajapati"


# I have created the below list to find the date on which the data was updated
# It will be used in the code to modify the "Publish_Date" column and change "Total_Views" to 0.
premiere_list = []
dataset_date=''

def extract_days(time_delta_str):
  try:
    days_str = time_delta_str.split()[0]
    return int(days_str)
  except (ValueError, IndexError):
    return 0

# Funtion to process column "Total_Views"
def parse_views(views_str):
    views_str = views_str.lower().replace(',', '').replace(' views', '').replace(' view', '').strip()
    view = views_str

    #This if-block checks for "million" views and "Premieres 'some_date' 'some_time' "
    if 'm' in view:
        temp = view.split('m')[0]
        try:
            temp = float(temp) * 1000000
            return temp
        except:
            x = view.split('premieres ')[-1]
            premiere_list.append(x.split(' ')[0])
            return 0

    #This elif-block checks for "thousand" views
    elif 'k' in view:
        temp = view.split('k')[0]
        try:
            temp = float(temp) * 1000
            return temp
        except:
            return 0

    #This elif-block checks for "No Views"
    elif view == "no":
        return 0

    #This else-block is just a check incase anything is left to be processed
    else:
        try:
            return float(view)
        except:
            return 0

# Funtion to process column "Publish_Date"
def parse_date(date_str):
    current_date = datetime.now().date()

    date_str = date_str.lower().replace('streamed ', '').replace('ago', '').strip()
    global dataset_date

    # Using the premiere_list to find the day on which dataset was last updated
    if len(premiere_list) > 0:
        for i in range(len(premiere_list)):
            premiere_list[i] = datetime.strptime(premiere_list[i], '%m/%d/%y')
        premiere_list.sort()
        # Subtracting '1' here to take the previous day of the earliest "Premiere Date"
        # This will give an approx. date of when the dataset would have been released
        dataset_date = premiere_list[0] - timedelta(days=1)
    else:
        # To handle the case where premiere_list is empty and all videos are released
        dataset_date = current_date-timedelta(days=700)

    if date_str == "":
        # Setting the publish_date according to when it is to be premiered
        x = premiere_list[0]
        premiere_list.pop()
        return x

    parts = date_str.split()
    if len(parts) != 2:
        return current_date

    value, unit = parts
    try:
        value = int(value)
    except ValueError:
        return current_date

    # Converting all dates into days, to make representaion easier 
    if 'year' in unit:
        return current_date - (dataset_date - timedelta(days=value*365))
    elif 'month' in unit:
        return current_date - (dataset_date - timedelta(days=value*30))
    elif 'week' in unit:
        return current_date - (dataset_date - timedelta(weeks=value))
    elif 'day' in unit:
        return current_date - (dataset_date - timedelta(days=value))
    elif 'hour' in unit:
        return current_date - (dataset_date - timedelta(hours=value/60))
    elif 'minute' in unit:
        return current_date - (dataset_date - timedelta(minutes=value/(24*60)))
    else:
        return current_date

# Funtion to process column "Channel_Link"
def parse_channel_link(link):
    return link.split('/')[-1]

def do_stuff(input_filename):

    #Loading CSV into a dictionary
    with open(input_filename, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = list(reader)

    # Processing row-wise using the created processing functions. 
    processed_data = []
    for row in data:
        processed_row = {
            'Total_Views': parse_views(row['Total_Views']),
            'Channel_Link': parse_channel_link(row['Channel_Link']),
            'Publish_Date': parse_date(row['Publish_Date'])
        }
        processed_data.append(processed_row)

    # 1. Line plot
    channels = {}
    for row in processed_data:
        channel = row['Channel_Link']
        if channel not in channels:
            channels[channel] = []
        channels[channel].append((row['Publish_Date'], row['Total_Views']))

    top_channels = sorted(channels.items(), key=lambda x: len(x[1]), reverse=True)[:3]

    plt.figure(figsize=(12, 6))
    for channel, videos in top_channels:
        dates, views = zip(*sorted(videos))
        dates=[date.days for date in dates]
        plt.plot(dates, views, marker='o', linestyle='-', label=channel)

    plt.xlabel('Publish Date')
    plt.ylabel('Total Views')
    plt.title('Total Views vs Publish Date for Top 3 Channels')
    x_ticks = plt.gca().get_xticks()
    x_labels = [f"{int(x)} days ago" for x in x_ticks]
    plt.gcf().autofmt_xdate()
    plt.gca().invert_xaxis()
    plt.xticks(x_ticks, x_labels)
    plt.legend()
    plt.savefig('lineplot.png')
    plt.close()

    # 2. Scatter plot
    plt.figure(figsize=(12, 6))
    publish_dates = []
    total_views = []
    i=0
    for row in processed_data:
        try:
          publish_dates.append(row['Publish_Date'].days)
        except:
          publish_dates.append(0)
        total_views.append(row['Total_Views'])

    plt.scatter(publish_dates, total_views, alpha=0.5)
    plt.xlabel('Publish Date')
    plt.ylabel('Total Views')
    plt.title('Total Views vs Publish Date (All Videos)')
    x_ticks = plt.gca().get_xticks()
    x_labels = [f"{int(x)} days ago" for x in x_ticks]
    plt.xticks(x_ticks, x_labels, rotation=45, ha='right')
    plt.gcf().autofmt_xdate()
    plt.gca().invert_xaxis()
    plt.savefig('scatterplot.png')
    plt.close()

    # 3. Bar chart
    channel_counts = {}
    for row in processed_data:
        channel = row['Channel_Link']
        channel_counts[channel] = channel_counts.get(channel, 0) + 1

    top_5_channels = sorted(channel_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    plt.figure(figsize=(10, 8))
    plt.pie([count for _, count in top_5_channels], 
			labels=[channel for channel, _ in top_5_channels],
			autopct='%1.1f%%',
			startangle=90)
    plt.title('Top 5 Most Productive Channels')
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    plt.tight_layout()
    plt.savefig('piechart.png')
    plt.close()

    # 4. Histogram
    current_date = datetime.now()
    video_ages = []
    global dataset_date
    dataset_date=datetime.combine(dataset_date, datetime.min.time())
    for row in processed_data:
        try:
          age_in_days = (current_date - dataset_date+row['Publish_Date']).days
        except:
          age_in_days = 0
        video_ages.append(age_in_days)
    plt.figure(figsize=(12, 6))
    plt.hist(video_ages, bins=20, edgecolor='black')
    plt.xlabel('Age (days)')
    plt.ylabel('Number of Videos')
    plt.title('Distribution of Video Ages')
    plt.savefig('histogram.png')
    plt.close()

if __name__ == '__main__':
    filename = "Kaggle_Youtube_DataSet.csv"
    do_stuff(filename)