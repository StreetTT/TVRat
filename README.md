# TVRat

This program allows you to manage a list of TV shows and their episodes in Notion.

## Set Up

1. Set Up Notion
	
	1. Create a [Notion Account](https://www.notion.so/product)
  	
	2. Create a copy of the [Template Database](https://valiant-silica-d27.notion.site/30f2b86983654c739a7d468b05282576?v=d00a920376604d39a56f271ba6c874a4) in your notion

1. Create Notion integration
  	
	3. Go to the [Integrations](https://www.notion.so/my-integrations) page in your Notion account.
  	
	4. Click the "New integration" button.
  	
	5. Give your integration a name and description.
  	
	6. Select "Private integration" as the integration type.
 	
	7. Click "Create integration".

3. Install Aplication
  	
	1. Clone the repository or download the program as a zip file. 
  	
	2. In the root directory of the program,  edit `Shows.txt` to contain the names of the TV shows you want to manage, each on a new line.
  	
	3. In the root directory of the program, edit `.env` and change the following environment variables: 
  	
	`notionToken`: Your Internal Integration Token, hiden in the new integration just created  
  
  	![image](https://user-images.githubusercontent.com/33423299/209343663-8be6a295-af39-45db-a4fe-bbbf1a21d404.png)
  
  	`databaseURL`: The URL of the coppied database where you want to store the show data.
  
  	![image](https://user-images.githubusercontent.com/33423299/209343918-ee700fd7-316e-4665-aed7-b59a0353f051.png)
   	
	4. Install the required dependencies by running `pip install -r requirements.txt.` in the root directory of the program

## How It Works

1. The program reads the names of the TV shows from the Shows.txt file and stores them in a list.

2. For each show in the list:

	1. The program searches for the show on TV Maze using the show's name.

	2. If the search is successful, it retrieves the show's data from TV Maze and stores it in a variable.

	3. The program retrieves the episodes data for the show from TV Maze.

	4. The program checks if the show already exists in the Notion database.

	5. If the show does not exist in the database, it creates a new page in the database with the show's data and episodes.

	6. If the show does exist in the database, it checks the most recent episode in the database and compares it to the episodes in the show data. If there are new episodes, it adds them to the database.

## Additional Notes

- The program will only add new episodes to the database if they have a higher season and episode number than the most recent episode in the database.

- The program makes use of the Notion and TV Maze APIs, which have rate limits. If the program fails due to rate limits, try running it again after a short wait.
