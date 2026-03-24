import streamlit as st
import pandas as pd
import io
import matplotlib.pyplot as plt
import datetime
import seaborn as sns

st.set_page_config(page_title="Nettoyeur de Données", layout="wide")

st.title("📊 Analyse et Nettoyage CSV")
st.write("Uploadez votre DataSet au format CSV pour effectuer une analyse exploratoire et un nettoyage automatique.")

today = datetime.date.today()
st.write(today)
# Widget pour uploader le fichier
uploaded_file = st.file_uploader("Choisissez un fichier CSV", type=["csv"])

if uploaded_file is not None:
    try:
        # Lecture du fichier CSV
        df = pd.read_csv(uploaded_file)
        
        # Séparer l'affichage en onglets
        tab1, tab2, tab3 = st.tabs(["📋 Données Brutes", "🔍 Analyse Exploratoire", "✨ Nettoyage Automatique"])
        
        with tab1:
            st.header("Aperçu du jeu de données")
            st.subheader("Head")
            st.dataframe(df.head())
            st.divider()

            st.subheader("Tail")
            st.dataframe(df.tail()) 

            st.divider()

            st.subheader("Description")
            st.dataframe(df.describe())
            st.divider()

            st.subheader("Info")
            buffer = io.StringIO()
            df.info(buf=buffer)
            st.text(buffer.getvalue())
            st.divider()

            
            st.subheader("Informations générales")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Nombre de Lignes", df.shape[0])
            col2.metric("Nombre de Colonnes", df.shape[1])
            col3.metric("Valeurs Manquantes Totales", df.isna().sum().sum())
            col4.metric("Lignes dupliquées", df.duplicated().sum().sum())
            
        with tab2:
            st.subheader("Statistiques Descriptives")
            st.dataframe(df.describe())

            st.subheader("Lignes dupliquées")

            l_dup = df.duplicated()
            
            if l_dup.any():
                st.dataframe(df[l_dup])
            else:
                st.info("Aucune ligne dupliquée n'est détectée")
            
            st.subheader("Valeurs Manquantes par Colonne")
            missing_data = df.isna().sum()
            missing_data = missing_data[missing_data > 0]
            if not missing_data.empty:
                st.bar_chart(missing_data)
            else:
                st.success("Aucune valeur manquante détectée !")
                
            ''' plt.figure(figsize=(10, 4))
            sns.boxplot(data=df, x='price') # Changed 'PRICE' to 'price'
            plt.xlabel('Prix des ferailles') # Changed label for better context
            plt.title("Boxplot des prix des ferailles") # Changed title for better context
            plt.show()'''
           
            st.subheader("Boîtes à moustache")
            numeric_df = df.select_dtypes(include=['number'])
            if not numeric_df.empty:
                col_box = st.selectbox("Choisir une variable pour la boîte à moustache", numeric_df.columns, key='boxplot_col')
                fig, ax = plt.subplots(figsize=(10,4))
                sns.boxplot(data=df, x=col_box, ax=ax)
                st.pyplot(fig)
            else:
                st.info("Aucune colonne numérique n'est disponible pour la boîte à moustache.")
            st.divider()

            st.subheader("Histogrammes")
            if not numeric_df.empty:
                col_hist = st.selectbox("Choisir une variable pour l'histogramme", numeric_df.columns, key='hist_col')
                fig, ax = plt.subplots(figsize=(10,4))
                sns.histplot(data=df, x=col_hist, ax=ax, kde=True, bins=50)
                st.pyplot(fig)
            else:
                st.info("Aucune colonne numérique n'est disponible pour l'histogramme.")
                
            st.divider()

            st.subheader("Nuage de points (Scatter Plot)")
            if len(numeric_df.columns) >= 2:
                col_x = st.selectbox("Axe X", numeric_df.columns, index=0, key='scatter_x')
                col_y = st.selectbox("Axe Y", numeric_df.columns, index=1, key='scatter_y')
                fig, ax = plt.subplots(figsize=(10,4))
                sns.scatterplot(data=df, x=col_x, y=col_y, ax=ax)
                st.pyplot(fig)
            else:
                st.info("Pas assez de colonnes numériques pour un nuage de points.")

            st.divider()
            
            st.subheader("Matrice de Corrélation")
            if len(numeric_df.columns) >= 2:
                fig, ax = plt.subplots(figsize=(10,8))
                sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
                st.pyplot(fig)
            else:
                st.info("Pas assez de colonnes numériques pour une matrice de corrélation.")

            st.divider()

            st.subheader("Types de Données")
            st.dataframe(df.dtypes.astype(str).reset_index().rename(columns={"index": "Colonne", 0: "Type"}))
            
            


        with tab3:
            st.subheader("Options de Nettoyage")
            
            st.markdown("#### Suppression de colonnes")
            cols_to_drop = st.multiselect("Sélectionnez les colonnes à supprimer", df.columns)
            
            st.markdown("#### Valeurs Aberrantes (Outliers)")
            handle_outliers = st.checkbox("Supprimer les outliers (méthode Z-score > 3 sur les colonnes numériques)", value=False)
            
            st.markdown("#### Doublons et Valeurs Manquantes")
            col_options1, col_options2 = st.columns(2)
            
            with col_options1:
                drop_duplicates = st.checkbox("Supprimer les doublons", value=True)
                handle_missing_num = st.selectbox(
                    "Stratégie pour valeurs manquantes (Numériques)",
                    ["Remplir avec la Médiane", "Remplir avec la Moyenne", "Remplir avec 0", "Supprimer les lignes"]
                )
                
            with col_options2:
                handle_missing_cat = st.selectbox(
                    "Stratégie pour valeurs manquantes (Catégorielles)",
                    ["Remplir avec le Mode (plus fréquent)", "Remplir avec 'Inconnu'", "Supprimer les lignes"]
                )
            
            if st.button("Lancer le Nettoyage", type="primary"):
                with st.spinner("Nettoyage en cours..."):
                    df_clean = df.copy()
                    
                    # 0. Supprimer des colonnes
                    if cols_to_drop:
                        df_clean = df_clean.drop(columns=cols_to_drop)
                    
                    # 1. Doublons
                    doublons_initiaux = df_clean.duplicated().sum()
                    if drop_duplicates:
                        df_clean = df_clean.drop_duplicates()
                    
                    # 1.5 Outliers
                    outliers_supprimes = 0
                    if handle_outliers:
                        numeric_cols = df_clean.select_dtypes(include=['number']).columns
                        lignes_avant = df_clean.shape[0]
                        for col in numeric_cols:
                            mean = df_clean[col].mean()
                            std = df_clean[col].std()
                            if std > 0:
                                df_clean = df_clean[abs((df_clean[col] - mean) / std) <= 3]
                        outliers_supprimes = lignes_avant - df_clean.shape[0]

                    # 2. Valeurs manquantes
                    for col in df_clean.columns:
                        if df_clean[col].isna().sum() > 0:
                            if pd.api.types.is_numeric_dtype(df_clean[col]):
                                if handle_missing_num == "Remplir avec la Médiane":
                                    df_clean[col] = df_clean[col].fillna(df_clean[col].median())
                                elif handle_missing_num == "Remplir avec la Moyenne":
                                    df_clean[col] = df_clean[col].fillna(df_clean[col].mean())
                                elif handle_missing_num == "Remplir avec 0":
                                    df_clean[col] = df_clean[col].fillna(0)
                                elif handle_missing_num == "Supprimer les lignes":
                                    df_clean = df_clean.dropna(subset=[col])
                            else:
                                if handle_missing_cat == "Remplir avec le Mode (plus fréquent)":
                                    if not df_clean[col].mode().empty:
                                        df_clean[col] = df_clean[col].fillna(df_clean[col].mode()[0])
                                elif handle_missing_cat == "Remplir avec 'Inconnu'":
                                    df_clean[col] = df_clean[col].fillna("Inconnu")
                                elif handle_missing_cat == "Supprimer les lignes":
                                    df_clean = df_clean.dropna(subset=[col])
                    
                    st.success("Nettoyage terminé avec succès !")
                    
                    # Rapport
                    st.write("### Rapport de Nettoyage")
                    col_r1, col_r2, col_r3 = st.columns(3)
                    col_r1.metric("Lignes restantes", df_clean.shape[0], delta=f"{df_clean.shape[0] - df.shape[0]} lignes")
                    col_r2.metric("Doublons supprimés", doublons_initiaux if drop_duplicates else 0)
                    col_r3.metric("Outliers supprimés", outliers_supprimes if handle_outliers else 0)
                    
                    st.write("### Aperçu des données nettoyées")
                    st.dataframe(df_clean.head(10))
                    
                    # Préparation du téléchargement CSV
                    csv = df_clean.to_csv(index=False).encode('utf-8')
                    
                    # Préparation du téléchargement Excel
                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                        df_clean.to_excel(writer, index=False, sheet_name='Data_Cleaned')
                    excel_data = excel_buffer.getvalue()
                    
                    col_dl1, col_dl2 = st.columns(2)
                    with col_dl1:
                        st.download_button(
                            label="📥 Télécharger en CSV",
                            data=csv,
                            file_name='dataset_nettoye.csv',
                            mime='text/csv',
                        )
                    with col_dl2:
                        st.download_button(
                            label="📥 Télécharger en Excel",
                            data=excel_data,
                            file_name='dataset_nettoye.xlsx',
                            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        )
                    
    except Exception as e:
        st.error(f"Une erreur s'est produite lors du traitement du fichier : {e}")
