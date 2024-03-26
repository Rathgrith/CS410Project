import { Container, TextInput, Title, Text, Button, MultiSelect, Paper, List, ListItem, ActionIcon, Pagination, Anchor } from '@mantine/core';
import { useState, useEffect } from "react";
import axios from "axios";
import { Trash } from 'tabler-icons-react';

function Homepage() {
    const [keywords, setKeywords] = useState("");
    const [selectedPapers, setSelectedPapers] = useState([]);
    const [allPapers, setAllPapers] = useState([]);
    const [paperSearchValue, setPaperSearchValue] = useState("");
    const [searchHistory, setSearchHistory] = useState(() => JSON.parse(localStorage.getItem("searchHistory")) || []);
    const [currentPage, setCurrentPage] = useState(1);
    const resultsPerPage = 10;

    useEffect(() => {
        localStorage.setItem("searchHistory", JSON.stringify(searchHistory));
    }, [searchHistory]);

    const submit = () => {
        const data = {
            keywords,
            selected_papers: selectedPapers,
        };
        setSearchHistory([...searchHistory, data]);
        axios.post(`http://localhost:8000/query`, data)
            .then((res) => {
                // Ensure allPapers is set to an array
                setAllPapers(Array.isArray(res.data) ? res.data : []);
            });
    };

    const deleteHistory = (index) => {
        const newHistory = searchHistory.filter((_, i) => i !== index);
        setSearchHistory(newHistory);
    };

    const clearHistory = () => {
        setSearchHistory([]);
    };

    const loadHistory = (history) => {
        setKeywords(history.keywords || "");
        setSelectedPapers(history.selected_papers || []);
    };

    const addToSelectedPapers = (paper) => {
        if (!selectedPapers.find(p => p.id === paper.id)) {
            setSelectedPapers([...selectedPapers, paper]);
        }
    };

    const paginateResults = (papers) => {
        if (!Array.isArray(papers)) {
            return [];  // Return an empty array if papers is not an array
        }
        const offset = (currentPage - 1) * resultsPerPage;
        return papers.slice(offset, offset + resultsPerPage);
    };

    return (
        <Container>
            <Title order={1} align="center" style={{ margin: '20px 0' }}>ArXiv Explorer</Title>
            <Text align="center">Search 2440876 papers!</Text>

            <TextInput
                label="Query"
                placeholder="Enter keywords here"
                value={keywords}
                onChange={(event) => setKeywords(event.target.value)}
            />
            <MultiSelect
                label="Related Papers"
                placeholder="Select the most relevant papers"
                searchValue={paperSearchValue}
                onSearchChange={setPaperSearchValue}
                data={selectedPapers}
                value={selectedPapers.map(p => p.title)}
                onChange={value => setSelectedPapers(allPapers.filter(p => value.includes(p.title)))}
                clearable
                searchable
            />
            <Button variant="filled" onClick={submit} style={{ marginBottom: '20px' }}>
                Search!
            </Button>

            <Paper style={{ padding: '20px', marginBottom: '20px' }}>
                <Title order={3}>Search Results</Title>
                <List>
                    {paginateResults(allPapers).map((paper, index) => (
                        <ListItem key={index}>
                            {paper.title}
                            <Anchor href={paper.url} target="_blank" style={{ marginLeft: 10 }}>View Paper</Anchor>
                            <Button onClick={() => addToSelectedPapers(paper)} size="xs" style={{ marginLeft: 5 }}>Add</Button>
                        </ListItem>
                    ))}
                </List>
                <Pagination 
                    page={currentPage} 
                    onChange={setCurrentPage} 
                    total={Math.ceil(allPapers.length / resultsPerPage)} 
                />
            </Paper>

            <Paper style={{ padding: '20px' }}>
                <Title order={3}>Search History</Title>
                <List>
                    {searchHistory.slice(-10).map((history, index) => (
                        <ListItem key={index} onClick={() => loadHistory(history)} style={{ cursor: 'pointer' }}>
                            Query: {history.keywords}, Papers: {(history.selected_papers || []).map(p => p.title).join(', ')}
                            <ActionIcon onClick={(e) => { e.stopPropagation(); deleteHistory(index); }}>
                                <Trash size={16} />
                            </ActionIcon>
                        </ListItem>
                    ))}
                </List>
                <Button onClick={clearHistory} color="red">Clear History</Button>
            </Paper>
        </Container>
    );
}

export default Homepage;
