import { Box, TextInput, Title, Text, Button, MultiSelect } from '@mantine/core';
import { useState, useEffect } from "react";
import axios from "axios";

function Homepage() {
    const [keywords, setKeywords] = useState("");
    const [selectedPapers, setSelectedPapers] = useState([]);

    const [allPapers, setAllPapers] = useState([]);
    const [paperSearchValue, setPaperSearchValue] = useState([]);

    useEffect(() => {
        axios.get(
            `http://localhost:8000/papers`
        )
        .then((res) => {
            console.log(res.data);
            setAllPapers(res.data);
        });
    }, []);

    
    useEffect(() => {
        if (paperSearchValue.length > 1) {
            // Every time `paperSearchValue` is updated, query backend to update the data to filter from.
            axios.get(
                `http://localhost:8000/papers?paper_query=${paperSearchValue}`
            )
            .then((res) => {
                console.log(res.data);
                setAllPapers(res.data);
            });
        }
    }, [paperSearchValue]);

    const submit = () => {
        const data = {
            keywords,
            selected_papers: selectedPapers,
        };
        axios.post(
            `http://localhost:8000/query`,
            { ...data }
        )
        .then((res) => {
            console.log(res.data);
        });
    };
    return (
    <Box style={{ 
        marginLeft: "20vw", 
        marginRight: "20vw", 
        marginTop: "30px"
    }}>
        <Title order={1}>ArXiv Explorer</Title>
        <Text>Search 2440876 papers!</Text>
        <TextInput
            label="Query"
            placeholder="Enter keywords here"
            value={keywords}
            onChange={(event)=>{setKeywords(event.target.value)}}
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
        <Button 
            variant="filled" 
            onClick={submit}
        >
            Search!
        </Button>
    </Box>
    );
}

export default Homepage;
