import { Box, TextInput, Title, Text, Button, Select, MultiSelect, Loader, Pagination, Stack, Card, Group, Badge, Anchor } from '@mantine/core';
import { useState, useEffect } from "react";
import axios from "axios";

function Homepage() {
    // Sessioning
    const [sessionId, setSessionId] = useState({ value: "New Session", label: "New Session" });
    const [allSessions, setAllSessions] = useState(["New Session"]);
    // Session History
    const [sessionHistory, setSessionHistory] = useState([]);
    // User query
    const [keywords, setKeywords] = useState("");
    const [selectedPapers, setSelectedPapers] = useState([]);
    // Values for selected paper dropdown
    const [allPapers, setAllPapers] = useState([]);
    const [paperSearchValue, setPaperSearchValue] = useState([]);
    // Results
    // Pagination
    const [itemsPerPage, setItemsPerPage] = useState(25);
    const [activePage, setPage] = useState(1);
    // Whether to show the Search Results section
    const [newSearch, setNewSearch] = useState(true);
    // Whether to show the loading bars
    const [searching, setSearching] = useState(false);
    // List of all papers
    const [resultPapers, setResultPapers] = useState([]);

    const renderSessionHistory = (data) => {
        setSessionHistory(data.map((item) => {
            return (
                <Card shadow="sm" padding="lg" radius="md" withBorder key={item.id}>
                    {item.query.keywords.length > 0 && (
                        <Group mb="xs">
                            <Text fw={700}>Keywords:</Text>
                            <Text size="sm" c="dimmed">
                                {item.query.keywords}
                            </Text>
                        </Group>
                    )}

                    {item.query.selected_papers.length > 0 && (
                        <Group mb="xs">
                            <Text fw={700}>Related Papers:</Text>
                            {item.query.selected_papers.map((v) => <Badge color="gray">{v}</Badge>)}
                        </Group>
                    )}
                </Card>
            )
        }));   
    }

    // Get all papers (first 1000) to search among for the relevant papers search dropdown
    useEffect(() => {
        axios.get(
            `http://localhost:8000/papers`
        )
        .then((res) => {
            setAllPapers(res.data);
        });
        axios.get(
            `http://localhost:8000/sessions`
        )
        .then((res) => {
            const preprocessedSessions = res.data.map((data) => ({ 
                value: data, 
                label: `Session ${data}` 
            }))
            preprocessedSessions.push({ 
                value: "New Session", 
                label: "New Session" 
            });
            setAllSessions(preprocessedSessions);
        });
        if (sessionId.value !== "New Session") {
            axios.get(
                `http://localhost:8000/session/${sessionId.value}`
            )
            .then((res) => {
                console.log(res.data);
                renderSessionHistory(res.data);
            });
        }
    }, []);

    // Update session metadata
    useEffect(() => {
        axios.get(
            `http://localhost:8000/sessions`
        )
        .then((res) => {
            const preprocessedSessions = res.data.map((data) => ({ 
                value: data, 
                label: `Session ${data}` 
            }))
            preprocessedSessions.push({ 
                value: "New Session", 
                label: "New Session" 
            });
            setAllSessions(preprocessedSessions);
        });
        if (sessionId.value !== "New Session") {
            axios.get(
                `http://localhost:8000/session/${sessionId.value}`
            )
            .then((res) => {
                renderSessionHistory(res.data);
            });
        };
    }, [resultPapers, sessionId]);

    // As the search gets refined, update the papers list to only include papers with the search term as a substring
    useEffect(() => {
        setNewSearch(true);
        if (paperSearchValue.length > 1) {
            // Every time `paperSearchValue` is updated, query backend to update the data to filter from.
            axios.get(
                `http://localhost:8000/papers`,
                { paper_query: paperSearchValue }
            )
            .then((res) => {
                setAllPapers(res.data);
            });
        }
    }, [paperSearchValue]);
    
    useEffect(() => {
        setNewSearch(true);
    }, [keywords]);

    // Send query (keywords and relevant papers) to the backend
    const submit = async () => {
        const data = {
            keywords,
            selected_papers: selectedPapers,
            session_id: sessionId.value === "New Session"? null : sessionId.value,
        };
        setSearching(true);
        setNewSearch(false);
        axios.get(
            `http://localhost:8000/query`,
            { 
                params: data,
                paramsSerializer: {
                    indexes: null, // no brackets at all
                } ,
            }
        )
        .then((response) => {
            setResultPapers(response.data.docs);
            setSessionId({ value: response.data.session_id, label: `Session ${response.data.session_id}` });
            setSearching(false);
        });
    };

    const items = resultPapers.slice((activePage-1)*itemsPerPage, (activePage)*itemsPerPage).map((item) => (
        <Card shadow="sm" padding="lg" radius="md" withBorder key={item.link}>
            <Anchor href={item.link} target="_blank">
                <Text fw={500}>{item.title}</Text>
            </Anchor>
            <Text size="xs" c="dimmed" mb="xs">
                {item.authors}
            </Text>

            <Text size="sm" c="dimmed" mb="xs">
                {item.abstract}
            </Text>

            <Group>
                <Badge color="blue" variant="light">Score: {Number((item.score).toFixed(3))}</Badge>
            </Group>
        </Card>
    ));

    const paperList = (
        <>
            <Stack>
                {items}
            </Stack>
            <Pagination total={resultPapers.length} value={activePage} onChange={setPage} mt="sm" />
        </>
    );

    return (
    <Box style={{ 
        marginLeft: "20vw", 
        marginRight: "20vw", 
        marginTop: "30px", 
        marginBottom: "30px"
    }}>
        <Text
            size="80px"
            fw={900} 
            order={1} 
            variant="gradient"
            gradient={{ from: 'blue', to: 'grape', deg: 90 }}
        >
            ArXiv Explorer
        </Text>
        <Text>Search 2M papers!</Text>
        <Select
            label="Session"
            key="session"
            defaultValue={"New Session"}
            allowDeselect={false}
            onChange={(_value, option) => setSessionId(option)}
            data={allSessions}
            disabled={searching}
        />
        <TextInput
            label="Query"
            key="query"
            placeholder="Enter keywords here"
            value={keywords}
            onChange={(event)=>{setKeywords(event.target.value)}}
            disabled={searching}
        />
        <MultiSelect
            label="Related Papers"
            key="papers"
            placeholder="Select the most relevant papers"
            searchValue={paperSearchValue}
            onSearchChange={setPaperSearchValue}
            limit={25}
            data={allPapers}
            value={selectedPapers}
            onChange={setSelectedPapers}
            disabled={searching}
            clearable
            searchable
        />
        <Button 
            variant="filled" 
            onClick={submit}
            disabled={searching}
        >
            Search!
        </Button>
        {!newSearch && <Title order={2}>Search Results</Title>}
        {!newSearch && searching && <Loader color="blue" type="bars" />}
        {!newSearch && !searching && (resultPapers.length? paperList : "No results found.")}
        {sessionHistory.length > 0 && <Title order={2}>Session History</Title>}
        {sessionHistory.length > 0 && <Stack>{sessionHistory}</Stack>}
    </Box>
    );
}

export default Homepage;