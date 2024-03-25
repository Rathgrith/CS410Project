import { Box, TextInput, Title, Text, Button, MultiSelect, Container, Grid, Paper, List, ListItem, ActionIcon, Pagination } from '@mantine/core';
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

    // useEffect(() => {
    //     axios.get(`http://localhost:8000/papers`)
    //         .then((res) => {
    //             setAllPapers(res.data);
    //         });
    // }, []);

    useEffect(() => {
        localStorage.setItem("searchHistory", JSON.stringify(searchHistory));
    }, [searchHistory]);

    const submit = () => {
        const data = {
            keywords,
            selected_papers: selectedPapers,
        };
        setSearchHistory([...searchHistory, { keywords, selectedPapers }]);
        axios.post(`http://localhost:8000/query`, data)
            .then((res) => {
                setAllPapers(res.data); // Assuming res.data is the array of papers returned by the search 
            });
    };

    const deleteHistory = (index) => {
        const newHistory = searchHistory.filter((_, i) => i !== index);
        setSearchHistory(newHistory);
    };

    const clearHistory = () => {
        setSearchHistory([]);
    };

    const paginateResults = (papers) => {
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
                limit={25}
                data={allPapers}
                value={selectedPapers}
                onChange={setSelectedPapers}
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
                        <ListItem key={index}>{paper.title}</ListItem>
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
                        <ListItem key={index}>
                            {history.keywords}
                            <ActionIcon onClick={() => deleteHistory(index)}>
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
