import mysql.connector
import pandas as pd

# from crud import mycursor

class DB:
    def __init__(self):
        # connect the database
        try:
            self.conn = mysql.connector.connect(
                host='127.0.0.1',
                user='root',
                password='9574982254',
                database='olympic'
            )
            self.mycursor = self.conn.cursor()
            print('Connection Established')
        except:
            print('Connection Error')

    def fecth_year(self):
        year = ['All']
        self.mycursor.execute('''
        SELECT DISTINCT(Year) FROM olympic.history
        ORDER BY Year ASC
        ''')

        data = self.mycursor.fetchall()

        for i in data:
            year.append(str(i[0]))

        return year


    def fetch_sport(self):
        sport = ['All']
        self.mycursor.execute('''
        SELECT DISTINCT(Sport) FROM olympic.history
        ORDER BY Sport ASC
        ''')

        data = self.mycursor.fetchall()

        for i in data:
            sport.append(i[0])

        return sport


    def fecth_all_country(self):
        countries = []
        self.mycursor.execute(
            '''
            SELECT DISTINCT(Team) FROM olympic.history
            '''
        )

        data = self.mycursor.fetchall()

        for i in data:
            countries.append(i[0])

        return countries


    def fecth_all_records(self,years,sports):

        if years == 0 and sports != 'All':
            self.mycursor.execute(f"""
                    SELECT * FROM olympic.history
                    WHERE Sport = '{sports}'
                    """)

        elif years != 0 and sports == 'All':
            self.mycursor.execute(f"""
                                SELECT * FROM olympic.history
                                WHERE Year = '{years}'
                                """)


        elif years != 0 and sports != 'All':
            self.mycursor.execute("""
                    SELECT * FROM olympic.history
                    WHERE Year = '{}' AND Sport = '{}'
                    """
                                  .format(years, sports))


        else:
            self.mycursor.execute(f"""
                                SELECT * FROM olympic.history
                                """)

        data = self.mycursor.fetchall()

        # Convert to DataFrame with column names
        df = pd.DataFrame(data, columns=[col[0] for col in self.mycursor.description])
        df = df.set_index('id')
        df['Year'] = df['Year'].astype(str)
        return df


    def fetch_all_male_records(self,years,sports,sex):
        self.mycursor.execute("""
                            SELECT * FROM olympic.history
                            WHERE Year = '{}' AND Sport = '{}' AND Sex = '{}'
                            """
                              .format(years, sports,sex))
        data = self.mycursor.fetchall()

        return data



    def fetch_all_geographic_records(self,Selected_c,Selected_y,Selected_s):
        df1 = self.fecth_all_records(0, 'All')



        # Handle cases where different combinations of selections are made
        if Selected_c == 'All':  # If "All" countries are selected
            if Selected_y == 'All':  # If "All" years are selected
                if Selected_s == 'All':  # If "All" sports are selected
                    # All data for all years, countries, and sports
                    Medals = df1[df1['Medal'].isin(['Gold', 'Silver', 'Bronze'])].groupby('Team').size().reset_index(
                        name='Medal Count'
                    )
                else:  # If a specific sport is selected
                    Medals = df1[df1['Medal'].isin(['Gold', 'Silver', 'Bronze'])]
                    Medals = Medals[Medals['Sport'] == Selected_s].groupby('Team').size().reset_index(
                        name='Medal Count'
                    )
            else:  # If a specific year is selected
                if Selected_s == 'All':  # If "All" sports are selected
                    Medals = df1[
                        (df1['Medal'].isin(['Gold', 'Silver', 'Bronze'])) &
                        (df1['Year'] == str(Selected_y))
                        ].groupby('Team').size().reset_index(name='Medal Count')
                else:  # If a specific sport is also selected
                    Medals = df1[
                        (df1['Medal'].isin(['Gold', 'Silver', 'Bronze'])) &
                        (df1['Year'] == str(Selected_y)) &
                        (df1['Sport'] == Selected_s)
                        ].groupby('Team').size().reset_index(name='Medal Count')
        else:  # If a specific country is selected
            if Selected_y == 'All':  # If "All" years are selected
                if Selected_s == 'All':  # If "All" sports are selected
                    Medals = df1[
                        (df1['Medal'].isin(['Gold', 'Silver', 'Bronze'])) &
                        (df1['Team'] == Selected_c)
                        ].groupby('Team').size().reset_index(name='Medal Count')
                else:  # If a specific sport is selected
                    Medals = df1[
                        (df1['Medal'].isin(['Gold', 'Silver', 'Bronze'])) &
                        (df1['Team'] == Selected_c) &
                        (df1['Sport'] == Selected_s)
                        ].groupby('Team').size().reset_index(name='Medal Count')
            else:  # If a specific year is selected
                if Selected_s == 'All':  # If "All" sports are selected
                    Medals = df1[
                        (df1['Medal'].isin(['Gold', 'Silver', 'Bronze'])) &
                        (df1['Team'] == Selected_c) &
                        (df1['Year'] == str(Selected_y))
                        ].groupby('Team').size().reset_index(name='Medal Count')
                else:  # If a specific sport is also selected
                    Medals = df1[
                        (df1['Medal'].isin(['Gold', 'Silver', 'Bronze'])) &
                        (df1['Team'] == Selected_c) &
                        (df1['Year'] == str(Selected_y)) &
                        (df1['Sport'] == Selected_s)
                        ].groupby('Team').size().reset_index(name='Medal Count')

        return Medals


    def fetch_country_distribution(self):
        team = []
        total_medal = []

        self.mycursor.execute(
            '''
            SELECT Team , COUNT(*) AS 'Total_Medal' FROM olympic.history
            WHERE Medal != 'None'
            GROUP BY Team
            ORDER BY Team ASC
            '''
        )

        data = self.mycursor.fetchall()

        for i in data:
            team.append(i[0])
            total_medal.append(i[1])

        return team,total_medal

    def fecth_all_male(self,selected_c,sex):

        self.mycursor.execute(
            '''
            SELECT COUNT(*) FROM olympic.history
            WHERE Sex = '{}' AND Team = '{}'
            GROUP BY Team
            ORDER BY Team ASC;
            '''
            .format(sex,selected_c)
        )

        data = self.mycursor.fetchall()

        return  data

    def fecth_all_played(self,selected_c,sex):

        self.mycursor.execute(
            '''
            SELECT COUNT(*) FROM olympic.history
            WHERE Sex = '{}' AND Team = '{}' AND Medal != 'None'
            GROUP BY Team
            ORDER BY Team ASC;
            '''
            .format(sex,selected_c)
        )

        data = self.mycursor.fetchall()

        return  data


    def fecth_year_medal(self):
        year = []
        medal = []

        self.mycursor.execute(
            '''
            SELECT Year , COUNT(*) FROM olympic.history
            WHERE Medal != 'None'
            GROUP BY Year
            ORDER BY Year ASC;
            '''
        )

        data = self.mycursor.fetchall()

        for i in data:
            year.append(i[0])
            medal.append(i[1])

        return year,medal



    def fecth_top_athelet(self):
        name = []
        medal = []
        self.mycursor.execute(
            '''
            SELECT Name, COUNT(*) AS 'Total' FROM olympic.history
            WHERE Medal != 'None'
            GROUP BY Name
            ORDER BY COUNT(*) DESC LIMIT 8
            '''
        )

        data = self.mycursor.fetchall()

        df = pd.DataFrame(data, columns=[col[0] for col in self.mycursor.description])
        # df = df.set_index('Name')
        return df






