import pandas as pd
import os

def main():
    # Data from OCHA 2022 Projections for BAY States
    data = [
        ["Adamawa", "Demsa", 275100], ["Adamawa", "Fufore", 323000], ["Adamawa", "Ganye", 262100],
        ["Adamawa", "Girei", 200200], ["Adamawa", "Gombi", 227900], ["Adamawa", "Guyuk", 272200],
        ["Adamawa", "Hong", 260900], ["Adamawa", "Jada", 259700], ["Adamawa", "Lamurde", 171600],
        ["Adamawa", "Madagali", 208400], ["Adamawa", "Maiha", 169900], ["Adamawa", "Mayo-Belwa", 235600],
        ["Adamawa", "Michika", 239400], ["Adamawa", "Mubi North", 233600], ["Adamawa", "Mubi South", 200400],
        ["Adamawa", "Numan", 141200], ["Adamawa", "Shelleng", 229000], ["Adamawa", "Song", 301000],
        ["Adamawa", "Toungo", 80500], ["Adamawa", "Yola North", 308000], ["Adamawa", "Yola South", 303000],
        ["Borno", "Abadam", 146600], ["Borno", "Askira/Uba", 210000], ["Borno", "Bama", 395800],
        ["Borno", "Bayo", 115900], ["Borno", "Biu", 257500], ["Borno", "Chibok", 97200],
        ["Borno", "Damboa", 341700], ["Borno", "Dikwa", 153900], ["Borno", "Gubio", 221700],
        ["Borno", "Guzamala", 140600], ["Borno", "Gwoza", 405200], ["Borno", "Hawul", 176900],
        ["Borno", "Jere", 306400], ["Borno", "Kaga", 131900], ["Borno", "Kala/Balge", 89100],
        ["Borno", "Konduga", 230500], ["Borno", "Kukawa", 297900], ["Borno", "Kwaya Kusar", 83100],
        ["Borno", "Mafa", 151800], ["Borno", "Magumeri", 205500], ["Borno", "Maiduguri", 791200],
        ["Borno", "Marte", 189600], ["Borno", "Mobbar", 170900], ["Borno", "Monguno", 160900],
        ["Borno", "Ngala", 346500], ["Borno", "Nganzai", 145200], ["Borno", "Shani", 148000],
        ["Yobe", "Bade", 219800], ["Yobe", "Bursari", 172500], ["Yobe", "Damaturu", 137900],
        ["Yobe", "Fika", 215000], ["Yobe", "Fune", 474700], ["Yobe", "Geidam", 244900],
        ["Yobe", "Gujba", 204100], ["Yobe", "Gulani", 162700], ["Yobe", "Jakusko", 365500],
        ["Yobe", "Karasuwa", 165900], ["Yobe", "Machina", 95900], ["Yobe", "Nangere", 137600],
        ["Yobe", "Nguru", 236900], ["Yobe", "Potiskum", 322100], ["Yobe", "Tarmua", 122100],
        ["Yobe", "Yunusari", 198000], ["Yobe", "Yusufari", 174100]
    ]

    df = pd.DataFrame(data, columns=["State", "LGA", "Total_Population_2022_Projection"])

    # Estimating School Age Population (Ages 5-17)
    # Based on MICS 6 and Demographic data, this is roughly 35% of total population in NE Nigeria
    school_age_ratio = 0.35
    df['Estimated_School_Age_Pop_5_17'] = (df['Total_Population_2022_Projection'] * school_age_ratio).astype(int)

    # Adding Out-of-School Indicators (State Level averages from MICS 6 2021)
    # Adamawa: 21.7%, Borno: 54.2%, Yobe: 62.9%
    out_of_school_map = {
        "Adamawa": 0.217,
        "Borno": 0.542,
        "Yobe": 0.629
    }
    df['Out_of_School_Rate'] = df['State'].map(out_of_school_map)
    df['Estimated_Out_of_School_Children'] = (df['Estimated_School_Age_Pop_5_17'] * df['Out_of_School_Rate']).astype(int)

    # Save to CSV
    os.makedirs('data/clean', exist_ok=True)
    clean_path = 'data/clean/north_east_population_lga.csv'
    df.to_csv(clean_path, index=False)
    print(f"Saved population data to {clean_path}")

if __name__ == "__main__":
    main()
