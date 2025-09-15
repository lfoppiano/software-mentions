package org.grobid.service;

import com.google.common.collect.ImmutableList;
import com.google.inject.Inject;
import com.google.inject.Singleton;
import org.grobid.core.main.GrobidHomeFinder;
import org.grobid.core.main.LibraryLoader;
import org.grobid.core.utilities.GrobidProperties;
import org.grobid.core.engines.tagging.GrobidCRFEngine;
import org.grobid.core.lexicon.SoftwareLexicon;
import org.grobid.service.configuration.SoftwareServiceConfiguration;
import org.grobid.core.utilities.SoftwareConfiguration;
import org.grobid.core.utilities.GrobidConfig.ModelParameters;

import java.io.*;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;


@Singleton
public class GrobidEngineInitialiser {
    private static final Logger LOGGER = LoggerFactory.getLogger(org.grobid.service.GrobidEngineInitialiser.class);

    @Inject
    public GrobidEngineInitialiser(SoftwareServiceConfiguration configuration) {
        LOGGER.info("Initialising Grobid");
        GrobidHomeFinder grobidHomeFinder = new GrobidHomeFinder(ImmutableList.of(configuration.getGrobidHome()));
        GrobidProperties.getInstance(grobidHomeFinder);
        SoftwareLexicon.getInstance();

        SoftwareConfiguration softwareConfiguration = null;
        try {
            ObjectMapper mapper = new ObjectMapper(new YAMLFactory());
            File configFile = new File("resources/config/config.yml");
            softwareConfiguration = mapper.readValue(new File(configFile.getAbsolutePath()), SoftwareConfiguration.class);
        } catch(Exception e) {
            LOGGER.error("The config file does not appear valid, see resources/config/config.yml", e);
            softwareConfiguration = null;
        }

        configuration.setSoftwareConfiguration(softwareConfiguration);

        if (softwareConfiguration != null && softwareConfiguration.getModels() != null) {
            for (ModelParameters model : softwareConfiguration.getModels()) 
                GrobidProperties.getInstance().addModel(model);
        }
        LibraryLoader.load();
    }
}
