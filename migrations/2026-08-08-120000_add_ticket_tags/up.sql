CREATE TABLE ticket
(
    channel         bigint  NOT NULL,
    guild           bigint  NOT NULL,
    tag             text,
    last_activity   bigint  NOT NULL,
    warned          boolean NOT NULL DEFAULT FALSE,
    PRIMARY KEY (channel)
);

CREATE INDEX ticket_guild_idx ON ticket (guild);
CREATE INDEX ticket_last_activity_idx ON ticket (last_activity);