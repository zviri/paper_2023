OCR_RESPONSES_FOLDER = os.environ.get("OCR_RESPONSES_FOLDER")

rule all:
    input:
        # "data/graph/retail_graph.pickle",
        "data/graph/retail_graph.gexf",
        "data/graph/business_graph.gexf",
        # "data/graph/business_graph_yearly.pickle",
        # "data/graph/business_graph_monthly.pickle",
        # "data/datasets/graph_retail.germ.txt",
        # "data/datasets/graph_business.germ.txt",
        "data/notebooks/check_retail_graph.ipynb",
        "data/datasets/graph_retail.germ.txt.4.200.out",
        "data/notebooks/retail_pattern_analysis.4.200.ipynb",
        "data/notebooks/check_business_graph.ipynb",
        # "data/datasets/graph_business.germ.txt.4.50.out",
        # "data/notebooks/business_pattern_analysis.4.50.ipynb",
        "data/datasets/graph_business.germ.txt.4.30.out",
        "data/notebooks/business_pattern_analysis.4.30.ipynb",
        "data/notebooks/check_both_graphs.ipynb",

rule extract_due_dates:
    output:
        "data/interim/due_dates.parquet"
    shell:
        """
        python -m experiments_lib.cli.extract_due_dates {OCR_RESPONSES_FOLDER} {output}
        """

rule build_graph:
    input:
        "data/interim/due_dates.parquet"
    output:
        nodes="data/graph/nodes.csv",
        edges="data/graph/edges.csv",
    shell:
        """
        python -m experiments_lib.cli.build_graph {input} {output.nodes} {output.edges}
        """

rule get_insolvency_data:
    output:
        "data/interim/insolvency_data.csv"
    shell:
        """
        python -m experiments_lib.cli.get_insolvency_data {output}
        """

rule retail_subgraph:
    input:
        nodes="data/graph/nodes.csv",
        edges="data/graph/edges.csv",
    output:
        "data/graph/retail_graph.pickle"  
    shell:
        """
        python -m experiments_lib.cli.get_retail_subgraph {input.nodes} {input.edges} {output}
        """

rule export_retail_graph_to_gephi:
    input:
        "data/graph/retail_graph.pickle"  
    output:
        "data/graph/retail_graph.gexf"  
    shell:
        """
        python -m experiments_lib.cli.export_to_gephi {input} {output}
        """

rule analyze_retail_graph:
    input:
        graph="data/graph/retail_graph.pickle",
        nodes="data/graph/nodes.csv",
        edges="data/graph/edges.csv",
        insolvency_data="data/interim/insolvency_data.csv",
    output:
         "data/notebooks/check_retail_graph.ipynb"
    shell:
        """
        mkdir -p data/notebooks
        papermill nb_templates/check_graph.ipynb -p graph_path {input.graph} -p nodes_path {input.nodes} -p edges_path {input.edges} -p insolvency_data_path {input.insolvency_data} {output} 
        """

rule business_subgraph:
    input:
        nodes="data/graph/nodes.csv",
        edges="data/graph/edges.csv",
    output:
        "data/graph/business_graph.pickle"  
    shell:
        """
        python -m experiments_lib.cli.get_business_subgraph {input.nodes} {input.edges} {output}
        """


rule export_business_graph_to_gephi:
    input:
        "data/graph/business_graph.pickle"  
    output:
        "data/graph/business_graph.gexf"  
    shell:
        """
        python -m experiments_lib.cli.export_to_gephi {input} {output}
        """

rule analyze_business_graph:
    input:
        graph="data/graph/business_graph.pickle",
        nodes="data/graph/nodes.csv",
        edges="data/graph/edges.csv",
        insolvency_data="data/interim/insolvency_data.csv"
    output:
         "data/notebooks/check_business_graph.ipynb"
    shell:
        """
        mkdir -p data/notebooks
        papermill nb_templates/check_graph.ipynb -p graph_path {input.graph} -p nodes_path {input.nodes} -p edges_path {input.edges} -p insolvency_data_path {input.insolvency_data} {output} 
        """

rule analyze_both_graphs:
    input:
        retail_graph_path="data/graph/retail_graph.pickle",
        business_graph_path="data/graph/business_graph.pickle",
        nodes="data/graph/nodes.csv"
    output:
         "data/notebooks/check_both_graphs.ipynb"
    shell:
        """
        mkdir -p data/notebooks
        papermill nb_templates/check_both_graphs.ipynb -p retail_graph_path {input.retail_graph_path} -p business_graph_path {input.business_graph_path} -p nodes_path {input.nodes} {output} 
        """

rule export_to_retail_graph_to_germ_format:
    input:
        "data/graph/retail_graph.pickle"
    output:
        germ="data/datasets/graph_retail.germ.txt",
        node_label_mapping="data/datasets/graph_retail.germ.node_labels.csv",
    shell:
        """
        python -m experiments_lib.cli.export_to_germ_format {input} {output.germ} --output_label_mapping {output.node_label_mapping}
        """

rule export_to_business_graph_to_germ_format:
    input:
        "data/graph/business_graph.pickle"
    output:
        germ="data/datasets/graph_business.germ.txt",
        node_label_mapping="data/datasets/graph_business.germ.node_labels.csv",
    shell:
        """
        python -m experiments_lib.cli.export_to_germ_format {input} {output.germ} --output_label_mapping {output.node_label_mapping}
        """

rule run_germ_on_retail_graph:
    input:
        germ="data/datasets/graph_retail.germ.txt",
    output:
        patterns="data/datasets/graph_retail.germ.txt.{num_edges}.{min_support}.out",
        projections="data/datasets/graph_retail.germ.txt.{num_edges}.{min_support}.out.projections",
        debtors="data/datasets/graph_retail.germ.txt.{num_edges}.{min_support}.out.debtors",
    shell:
        """
        python -m gspan_mining.main -s {wildcards.min_support} -e {wildcards.num_edges} -d 1 --debtor_support 1 {input.germ} {output.patterns}
        """

rule analyze_retail_patterns:
    input:
        germ_output="data/datasets/graph_retail.germ.txt.{num_edges}.{min_support}.out",
        node_label_mapping="data/datasets/graph_retail.germ.node_labels.csv",
        nodes="data/graph/nodes.csv",
        edges="data/graph/edges.csv",
        debtors="data/datasets/graph_retail.germ.txt.{num_edges}.{min_support}.out.debtors",
        insolvency_data="data/interim/insolvency_data.csv",
    output:
        patterns="data/notebooks/retail_pattern_analysis.{num_edges}.{min_support}.ipynb",
    shell:
        """
        papermill nb_templates/analyze_retail_patterns.ipynb -p germ_output_path {input.germ_output} -p node_label_mapping_path {input.node_label_mapping} -p nodes_path {input.nodes} -p edges_path {input.edges} -p debtors_path {input.debtors} -p insolvency_data_path {input.insolvency_data} {output} 
        """

rule run_germ_on_business_graph:
    input:
        germ="data/datasets/graph_business.germ.txt",
    output:
        patterns="data/datasets/graph_business.germ.txt.{num_edges}.{min_support}.out",
        projections="data/datasets/graph_business.germ.txt.{num_edges}.{min_support}.out.projections",
        debtors="data/datasets/graph_business.germ.txt.{num_edges}.{min_support}.out.debtors",
    shell:
        """
        python -m gspan_mining.main -s {wildcards.min_support} -e {wildcards.num_edges} -d 1 --debtor_support 1 {input.germ} {output.patterns}
        """

rule analyze_business_patterns:
    input:
        germ_output="data/datasets/graph_business.germ.txt.{num_edges}.{min_support}.out",
        node_label_mapping="data/datasets/graph_business.germ.node_labels.csv",
        nodes="data/graph/nodes.csv",
        edges="data/graph/edges.csv",
        debtors="data/datasets/graph_business.germ.txt.{num_edges}.{min_support}.out.debtors",
        insolvency_data="data/interim/insolvency_data.csv"
    output:
        patterns="data/notebooks/business_pattern_analysis.{num_edges}.{min_support}.ipynb",
    shell:
        """
        papermill -k nb_templates/analyze_business_patterns.ipynb -p germ_output_path {input.germ_output} -p node_label_mapping_path {input.node_label_mapping} -p nodes_path {input.nodes} -p edges_path {input.edges} -p debtors_path {input.debtors} -p insolvency_data_path {input.insolvency_data} {output} 
        """