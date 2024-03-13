import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import csv

file_path = 'result.csv'

class Vertice:
    def __init__(self, valor):
        self.valor = valor
        self.adjacentes = []

class Aresta:
    def __init__(self, vertice_origem, vertice_destino, relation):
        self.vertice_origem = vertice_origem
        self.vertice_destino = vertice_destino
        self.relation = relation

class Grafo:
    def __init__(self):
        self.vertices = []
        self.arestas = []

    def numVertices(self):
        return len(self.vertices)

    def numArestas(self):
        return len(self.arestas)

    def grau(self, vertice):
        return sum(1 for aresta in self.arestas if vertice in (aresta.vertice_origem, aresta.vertice_destino))

    def verticesAdjacentes(self, vertice):
        adjacentes = []
        for aresta in self.arestas:
            if aresta.vertice_origem == vertice:
                adjacentes.append(aresta.vertice_destino)
            elif aresta.vertice_destino == vertice:
                adjacentes.append(aresta.vertice_origem)
        return adjacentes

    def arestasIncidentes(self, vertice):
        arestas = []
        for aresta in self.arestas:
            if aresta.vertice_origem == vertice or aresta.vertice_destino == vertice:
                arestas.append(aresta)
        return arestas

    def saoAdjacentes(self, vertice1, vertice2):
        return vertice2 in vertice1.adjacentes

    def adicionaVertice(self, valor):
        vertice = Vertice(valor)
        self.vertices.append(vertice)
        return vertice
    
    def adicionaAresta(self, vertice_origem, vertice_destino, relation):
        aresta = Aresta(vertice_origem, vertice_destino, relation)
        self.arestas.append(aresta)
        vertice_origem.adjacentes.append(vertice_destino)
        vertice_destino.adjacentes.append(vertice_origem)
    
    def insereVertice(self, valor):
        vertice = Vertice(valor)
        self.vertices.append(vertice)
        with open(file_path, 'a', newline='') as csvfile:
            fieldnames = ['head', 'relation', 'tail']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'head': vertice.valor, 'relation': '', 'tail': ''})
        return vertice

    def insereAresta(self, vertice_origem, vertice_destino, relation):
        aresta = Aresta(vertice_origem, vertice_destino, relation)
        self.arestas.append(aresta)
        vertice_origem.adjacentes.append(vertice_destino)
        vertice_destino.adjacentes.append(vertice_origem)
        with open(file_path, 'a', newline='') as csvfile:
            fieldnames = ['head', 'relation', 'tail']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'head': vertice_destino.valor, 'relation': relation, 'tail': vertice_destino.valor})
        return pd.read_csv(file_path)

    def removeVertice(self, valor):
        vertices_to_remove = [v for v in self.vertices if v.valor == valor]
        for vertice in vertices_to_remove:
            self.vertices.remove(vertice)
            for v in self.vertices:
                if vertice in v.adjacentes:
                    v.adjacentes.remove(vertice)
            for aresta in self.arestas:
                if aresta.vertice_origem == vertice or aresta.vertice_destino == vertice:
                    self.arestas.remove(aresta)
        self.escreverCSV(file_path, grafo)
        return pd.read_csv(file_path)

    def removeAresta(self, aresta):
        self.arestas.remove(aresta)
        aresta.vertice_origem.adjacentes.remove(aresta.vertice_destino)
        aresta.vertice_destino.adjacentes.remove(aresta.vertice_origem)

    def escreverCSV(self, arquivo, grafo):
        with open(arquivo, 'w', newline='') as csvfile:
            fieldnames = ['head', 'relation', 'tail']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for aresta in grafo.arestas:
                writer.writerow({'head': aresta.vertice_origem.valor, 'relation': aresta.relation, 'tail': aresta.vertice_destino.valor})

def lerCSV(arquivo):
    grafo = Grafo()
    vertices = {}
    with open(arquivo, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            head = row['head']
            tail = row['tail']
            relation = row['relation']

            if head not in vertices:
                vertice_origem = grafo.adicionaVertice(head)
                vertices[head] = vertice_origem
            else:
                vertice_origem = vertices[head]
            
            if tail not in vertices:
                vertice_destino = grafo.adicionaVertice(tail)
                vertices[tail] = vertice_destino
            else:
                vertice_destino = vertices[tail]
                
            grafo.adicionaAresta(vertice_origem, vertice_destino, relation)
    return grafo

def update_graph(G):
    pos = nx.spring_layout(G, k=0.5)

    node_trace = go.Scatter(
        x=[], y=[],
        mode='markers+text',
        hoverinfo='text',
        text=[],
        marker=dict(
            showscale=False,
            colorscale='YlGnBu',
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))
    for node, (x, y) in pos.items():
        node_trace['x'] += (x,)
        node_trace['y'] += (y,)
        node_trace['text'] += (node,)
        node_trace['marker']['color'] += (len(list(G.neighbors(node))),)

    edge_x = []
    edge_y = []
    edge_text = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_text.extend([G[edge[0]][edge[1]]['label'], ''])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='text',
        mode='lines')

    edge_trace.text = edge_text

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='<br>Knowledge Graph',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        annotations=[dict(
                            text="",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    return fig

st.set_page_config(layout="wide")

plot_placeholder = st.empty()

grafo = lerCSV(file_path)

result_df = pd.read_csv(file_path)

all_relations = result_df["relation"].unique()
selected_relations = st.sidebar.multiselect("Filtros", all_relations, default=all_relations)
selected_relations = [relation for relation in selected_relations if pd.notna(relation)]
print(selected_relations)
search_query = st.sidebar.text_input("Search")

if selected_relations:
    df_filtered = result_df[result_df["relation"].isin(selected_relations)]

    if search_query:
        search_result = df_filtered[df_filtered['head'].str.contains(search_query, case=False) | df_filtered['tail'].str.contains(search_query, case=False)]
        if not search_result.empty:
            df_filtered = search_result
        else:
            st.warning("Não foram encontrados vértices para a busca.")

    G = nx.Graph()
    for _, row in df_filtered.iterrows():
        if row['relation'] != '':
            G.add_edge(row['head'], row['tail'], label=row['relation'])


    pos = nx.spring_layout(G, k=0.5)

    node_trace = go.Scatter(
        x=[], y=[],
        mode='markers+text',
        hoverinfo='text',
        text=[],
        marker=dict(
            showscale=False,
            colorscale='YlGnBu',
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2))

    for node, (x, y) in pos.items():
        node_trace['x'] += (x,)
        node_trace['y'] += (y,)
        node_trace['text'] += (node,)
        node_trace['marker']['color'] += (len(list(G.neighbors(node))),)

    edge_x = []
    edge_y = []
    edge_text = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_text.extend([G[edge[0]][edge[1]]['label'], ''])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='text',
        mode='lines')

    edge_trace.text = edge_text

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title='<br>Knowledge Graph',
                        titlefont_size=16,
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        annotations=[dict(
                            text="",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
    
    plot_placeholder.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    col1.metric("Número de vértices", grafo.numVertices())

    col2.metric("Número de arestas", grafo.numArestas())

    st.sidebar.subheader("Operações no Grafo")
    opcao_operacao = st.sidebar.selectbox("Selecione uma operação", ["Adicionar Vértice", "Adicionar Aresta", "Remover Vértice", "Remover Aresta"])

    if opcao_operacao == "Adicionar Vértice":
        novo_vertice_valor = st.sidebar.text_input("Valor do Novo Vértice")
        if st.sidebar.button("Adicionar Vértice") and novo_vertice_valor:
            vertice_adicionado = grafo.insereVertice(novo_vertice_valor)
            st.success(f"Vértice '{novo_vertice_valor}' adicionado com sucesso!")

            G = nx.Graph()
            for _, row in df_filtered.iterrows():
                if row['relation'] != '':
                    G.add_edge(row['head'], row['tail'], label=row['relation'])

            G.add_node(vertice_adicionado.valor)

            updated_fig = update_graph(G)
            plot_placeholder.plotly_chart(updated_fig, use_container_width=True)

    elif opcao_operacao == "Adicionar Aresta":
        novo_origem_valor = st.sidebar.text_input("Valor do Vértice Origem")
        novo_destino_valor = st.sidebar.text_input("Valor do Vértice Destino")
        nova_relacao = st.sidebar.text_input("Relação da Aresta")
        if st.sidebar.button("Adicionar Aresta") and novo_origem_valor and novo_destino_valor and nova_relacao:
            vertice_origem = next((v for v in grafo.vertices if v.valor == novo_origem_valor), None)
            vertice_destino = next((v for v in grafo.vertices if v.valor == novo_destino_valor), None)
            if vertice_origem and vertice_destino:
                if vertice_origem not in G.nodes:
                    G.add_node(vertice_origem.valor)
                if vertice_destino not in G.nodes:
                    G.add_node(vertice_destino.valor)
                G.add_edge(vertice_origem.valor, vertice_destino.valor, label=nova_relacao)
                st.success(f"Aresta adicionada entre '{novo_origem_valor}' e '{novo_destino_valor}' com relação '{nova_relacao}'!")
                updated_fig = update_graph(G)
                plot_placeholder.plotly_chart(updated_fig, use_container_width=True)

                grafo.insereAresta(vertice_origem, vertice_destino, nova_relacao)
            else:
                st.warning("Um ou ambos os vértices não foram encontrados.")

    elif opcao_operacao == "Remover Vértice":
        vertice_para_remover_valor = st.sidebar.text_input("Valor do Vértice para Remover")
        if st.sidebar.button("Remover Vértice") and vertice_para_remover_valor:
            df_filtered = grafo.removeVertice(vertice_para_remover_valor)
            if not df_filtered.empty:
                st.success(f"Vértice '{vertice_para_remover_valor}' removido com sucesso!")

                G = nx.Graph()
                for _, row in df_filtered.iterrows():
                    if row['relation'] != '':
                        G.add_edge(row['head'], row['tail'], label=row['relation'])

                updated_fig = update_graph(G)
                plot_placeholder.plotly_chart(updated_fig, use_container_width=True)
            else:
                st.warning(f"Nenhum vértice removido com o valor '{vertice_para_remover_valor}'.")

    elif opcao_operacao == "Remover Aresta":
        aresta_para_remover_origem = st.sidebar.text_input("Valor do Vértice de Origem da Aresta")
        aresta_para_remover_destino = st.sidebar.text_input("Valor do Vértice de Destino da Aresta")
        if st.sidebar.button("Remover Aresta") and aresta_para_remover_origem and aresta_para_remover_destino:
            df_filtered = grafo.removeAresta(aresta_para_remover_origem, aresta_para_remover_destino)
            if not df_filtered.empty:
                st.success(f"Aresta entre '{aresta_para_remover_origem}' e '{aresta_para_remover_destino}' removida com sucesso!")

                G = nx.Graph()
                for _, row in df_filtered.iterrows():
                    if row['relation'] != '':
                        G.add_edge(row['head'], row['tail'], label=row['relation'])

                updated_fig = update_graph(G)
                plot_placeholder.plotly_chart(updated_fig, use_container_width=True)
            else:
                st.warning(f"Nenhuma aresta entre '{aresta_para_remover_origem}' e '{aresta_para_remover_destino}' encontrada.")
    st.sidebar.subheader("Checar Informações de Vértices")
    opcao_vertice = st.sidebar.selectbox("Selecione uma opção", ["Grau do Vértice", "Vértices Adjacentes", "Verificar Adjacência", "Arestas Incidentes"])

    if opcao_vertice == "Grau do Vértice":
        vertice_nome = st.sidebar.text_input("Nome do Vértice")
        if st.sidebar.button("Checar Grau") and vertice_nome:
            vertice = next((v for v in grafo.vertices if v.valor == vertice_nome), None)
            if vertice:
                grau = grafo.grau(vertice)
                st.sidebar.success(f"O grau do vértice '{vertice_nome}' é {grau}.")
            else:
                st.sidebar.warning(f"Vértice '{vertice_nome}' não encontrado no grafo.")

    elif opcao_vertice == "Vértices Adjacentes":
        vertice_nome = st.sidebar.text_input("Nome do Vértice")
        if st.sidebar.button("Checar Adjacentes") and vertice_nome:
            vertice = next((v for v in grafo.vertices if v.valor == vertice_nome), None)
            if vertice:
                adjacentes = grafo.verticesAdjacentes(vertice)
                if adjacentes:
                    st.sidebar.success(f"Os vértices adjacentes a '{vertice_nome}' são: {', '.join([v.valor for v in adjacentes])}.")
                else:
                    st.sidebar.warning(f"Não há vértices adjacentes a '{vertice_nome}'.")
            else:
                st.sidebar.warning(f"Vértice '{vertice_nome}' não encontrado no grafo.")

    elif opcao_vertice == "Verificar Adjacência":
        vertice1_nome = st.sidebar.text_input("Nome do Vértice 1")
        vertice2_nome = st.sidebar.text_input("Nome do Vértice 2")
        if st.sidebar.button("Verificar Adjacência") and vertice1_nome and vertice2_nome:
            vertice1 = next((v for v in grafo.vertices if v.valor == vertice1_nome), None)
            vertice2 = next((v for v in grafo.vertices if v.valor == vertice2_nome), None)
            if vertice1 and vertice2:
                adjacencia = grafo.saoAdjacentes(vertice1, vertice2)
                if adjacencia:
                    st.sidebar.success(f"'{vertice1_nome}' e '{vertice2_nome}' são adjacentes.")
                else:
                    st.sidebar.warning(f"'{vertice1_nome}' e '{vertice2_nome}' não são adjacentes.")
            else:
                st.sidebar.warning(f"Um ou ambos os vértices não foram encontrados.")

    elif opcao_vertice == "Arestas Incidentes":
        vertice_nome = st.sidebar.text_input("Nome do Vértice")
        if st.sidebar.button("Checar Arestas Incidentes") and vertice_nome:
            vertice = next((v for v in grafo.vertices if v.valor == vertice_nome), None)
            if vertice:
                arestas_incidentes = grafo.arestasIncidentes(vertice)
                if arestas_incidentes:
                    arestas_info = ", ".join([f"({a.vertice_origem.valor} - {a.relation} - {a.vertice_destino.valor})" for a in arestas_incidentes])
                    st.sidebar.success(f"As arestas incidentes a '{vertice_nome}' são: {arestas_info}.")
                else:
                    st.sidebar.warning(f"Não há arestas incidentes a '{vertice_nome}'.")
            else:
                st.sidebar.warning(f"Vértice '{vertice_nome}' não encontrado no grafo.")



else:
    df_filtered = result_df
    st.warning("Selecione pelo menos um filtro")
