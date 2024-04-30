import { Box, TextInput, Title, Text, Button, Select, MultiSelect, Loader, Pagination, Stack, Card, Group, Badge, Anchor, ScrollArea, Space, Modal, NumberInput } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useState, useEffect, useRef } from "react";
import axios from "axios";

function Homepage() {
    const [opened, { open, close }] = useDisclosure(false);
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
    const [itemsPerPage, setItemsPerPage] = useState(10);
    const [activePage, setPage] = useState(1);
    // Whether to show the Search Results section
    const [newSearch, setNewSearch] = useState(true);
    // Whether to show the loading bars
    const [searching, setSearching] = useState(false);
    // List of all papers
    const [resultPapers, setResultPapers] = useState([]);
    // List of recommended papers
    const [recPapers, setRecPapers] = useState([]);
    // Algorithm weights
    const [faiss, setFAISS] = useState(3);
    const [hits, setHITS] = useState(1);

    // Function to handle keyword click
    const handleKeywordClick = (query) => {
        setKeywords(query.keywords);
        setFAISS(query.faiss_weight);
        setHITS(query.hits_weight);
        setSelectedPapers(query.selected_papers);
        submit(query);
    }

    // Handle Delete
    const handleDelete = (id) => {
        axios.get(
            `http://localhost:8000/delete_session_history/${sessionId.value}/${id}`
        )
            .then((res) => {
                renderSessionHistory(res.data);
            });
    }

    const renderSessionHistory = (data) => {
        setSessionHistory(data.map((item) => {
            return (
                <Card shadow="sm" padding="lg" radius="md" withBorder key={item.id}>
                    {item.query.keywords.length > 0 && (
                        <Group mb="xs" style={{ cursor: 'pointer' }} onClick={() => handleKeywordClick(item.query)}>
                            <Text fw={700}>Keywords:</Text>
                            <Badge color="gray">
                                {item.query.keywords}
                            </Badge>
                        </Group>
                    )}
                    {item.query.faiss_weight != null && item.query.hits_weight && (
                        <Group mb="xs" style={{ cursor: 'pointer' }} onClick={() => handleKeywordClick(item.query)}>
                            <Text fw={700}>Weights:</Text>
                            <Badge color="gray">Faiss={item.query.faiss_weight}, HITS={item.query.hits_weight}</Badge>
                        </Group>
                    )}
                    {item.query.selected_papers.length > 0 && (
                        <Group mb="xs" style={{ cursor: 'pointer' }} onClick={() => handleKeywordClick(item.query)}>
                            <Text fw={700}>Related Papers:</Text>
                            {item.query.selected_papers.map((v, i) => <Badge color="gray" key={i}>{v}</Badge>)}
                        </Group>
                    )}
                    <Button color="grey" size="xs" onClick={() => handleDelete(item.id)}>Delete</Button>
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
        axios.get(
            `http://localhost:8000/papers/recommend`
        )
            .then((res) => {
                setRecPapers(res.data);
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
        } else {
            renderSessionHistory([]);
        }
    }, []);

    // Update session metadata
    useEffect(() => {
        const session_id = sessionId.value === "New Session" ? -1 : sessionId.value
        setRecPapers([]);
        axios.get(
            `http://localhost:8000/papers/recommend`,
            {
                params: { session_id },
                paramsSerializer: {
                    indexes: null, // no brackets at all
                },
            }
        )
            .then((res) => {
                setRecPapers(res.data);
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
            ).then((res) => {
                renderSessionHistory(res.data);
            });
        } else {
            renderSessionHistory([]);
        }
    }, [resultPapers, sessionId]);

    // As the search gets refined, update the papers list to only include papers with the search term as a substring
    useEffect(() => {
        setNewSearch(true);
        if (paperSearchValue.length > 1) {
            // Every time `paperSearchValue` is updated, query backend to update the data to filter from.
            axios.get(
                `http://localhost:8000/papers`,
                {
                    params: { paper_query: paperSearchValue },
                    paramsSerializer: {
                        indexes: null, // no brackets at all
                    },
                }
            )
                .then((res) => {
                    setAllPapers(res.data);
                });
        }
    }, [paperSearchValue]);

    useEffect(() => {
        setNewSearch(true);
    }, [keywords]);

    const saveInteraction = (paper_id) => {
        const session_id = sessionId.value === "New Session" ? -1 : sessionId.value;
        axios.get(
            `http://localhost:8000/session/${session_id}/select/${paper_id}`,
        );
    };

    // Send query (keywords and relevant papers) to the backend
    const submit = async (query) => {
        const data = {
            keywords: query?.keywords ?? keywords,
            selected_papers: query?.selected_papers ?? selectedPapers,
            session_id: sessionId.value === "New Session" ? null : sessionId.value,
            faiss_weight: query?.faiss_weight ?? faiss,
            hits_weight: query?.hits_weight ?? hits,
        };
        setSearching(true);
        setNewSearch(false);
        axios.get(
            `http://localhost:8000/query`,
            {
                params: data,
                paramsSerializer: {
                    indexes: null, // no brackets at all
                },
            }
        )
            .then((response) => {
                setResultPapers(response.data.docs);
                setSessionId({ value: response.data.session_id, label: `Session ${response.data.session_id}` });
                setSearching(false);
            });

        const session_id = sessionId.value === "New Session" ? -1 : sessionId.value;
        setRecPapers([]);
        axios.get(
            `http://localhost:8000/papers/recommend`,
            {
                params: { session_id },
                paramsSerializer: {
                    indexes: null, // no brackets at all
                },
            }
        )
            .then((res) => {
                setRecPapers(res.data);
            });
    };

    const items = resultPapers.slice((activePage - 1) * itemsPerPage, (activePage) * itemsPerPage).map((item) => (
        <Card shadow="sm" padding="lg" radius="md" withBorder key={item.link}>
            <Anchor onClick={() => { saveInteraction(item.id) }} href={item.link} target="_blank">
                <Text fw={500}>{item.title}</Text>
            </Anchor>

            <ScrollArea mah={50}>
                <Text size="xs" c="dimmed" mb="xs">
                    {item.authors}
                </Text>
            </ScrollArea>

            <ScrollArea mah={150}>
                <Text size="sm" c="dimmed" mb="xs">
                    {item.abstract}
                </Text>
            </ScrollArea>

            <Space h="md" />
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
            <Pagination total={resultPapers.length / itemsPerPage} value={activePage} onChange={setPage} mt="sm" />
        </>
    );

    const recPapersList = (
        <>
            <Stack gap="xs">
                {recPapers.map((item) => (
                    <Anchor onClick={() => { saveInteraction(item.id) }} href={item.link} target="_blank">
                        <Text size="sm">{item.title}</Text>
                    </Anchor>
                ))}
            </Stack>
        </>
    );
    const onSessionDelete = function () {
        axios.get(
            `http://localhost:8000/delete_session/${sessionId.value}`
        ).then(() => {
            axios.get(
                `http://localhost:8000/sessions`
            ).then((res) => {
                const preprocessedSessions = res.data.map((data) => ({
                    value: data,
                    label: `Session ${data}`
                }));
                preprocessedSessions.push({
                    value: "New Session",
                    label: "New Session"
                });
                setAllSessions(preprocessedSessions);
                setSessionHistory([]);
                setSessionId({ value: "New Session", label: "New Session" });
            });
        }
        )

    }
    return (
        <Box style={{
            marginLeft: "20vw",
            marginRight: "20vw",
            marginTop: "30px",
            marginBottom: "30px"
        }}>
            <Modal opened={opened} onClose={close} title="Search Settings">
                The score used to rank the documents is based on the assigned score from a variety of algorithms. You can adjust the weight multipliers here to adjust the consideration given to each algorithms' score.
                <NumberInput
                    label="FAISS Search Score Weight"
                    value={faiss} onChange={setFAISS}
                    allowNegative={false}
                />
                <NumberInput
                    label="HITS Score Weight"
                    value={hits} onChange={setHITS}
                    allowNegative={false}
                />
            </Modal>
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
                onChange={(value, option) => {
                    setSessionId(option);
                }}
                data={allSessions}
                disabled={searching}
            />

            {recPapers.length > 0 && <Space h="md" />}
            {recPapers.length > 0 && <Title order={2}>Recommendations</Title>}
            {recPapers.length > 0 && recPapersList}
            {recPapers.length > 0 && <Space h="md" />}

            <TextInput
                label="Query"
                key="query"
                placeholder="Enter keywords here"
                value={keywords}
                onChange={(event) => { setKeywords(event.target.value); }}
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
            <Space h="md" />
            <Group justify="space-between">
                <Button
                    variant="filled"
                    onClick={() => submit()}
                    disabled={searching}
                >
                    Search!
                </Button>

                <Button
                    variant="outline"
                    onClick={open}
                >
                    Search Settings
                </Button>
            </Group>

            {!newSearch && <Space h="md" />}
            {!newSearch && <Title order={2}>Search Results</Title>}
            {!newSearch && searching && <Loader color="blue" type="bars" />}
            {!newSearch && !searching && (resultPapers.length ? paperList : "No results found.")}

            {sessionHistory.length > 0 &&
                <>
                    <Space h="md" />
                    <Group justify="space-between">
                        <Title order={2}>Session History</Title>
                        <Text>Session #{sessionId.value} - <span onClick={onSessionDelete} style={{ cursor: 'pointer', color: 'blue', textDecoration: 'underline' }}>Delete</span></Text>
                    </Group>
                    <Stack>{sessionHistory}</Stack>
                </>
            }
        </Box>
    );
}

export default Homepage;