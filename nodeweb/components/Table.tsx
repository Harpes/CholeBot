import Link from '@material-ui/core/Link';
import { createStyles, Theme, WithStyles, withStyles } from '@material-ui/core/styles';
import React from 'react';

import { getBossDisplayName, Mems, Recs, recType, toThousands } from '../utils';

const styles = (_: Theme) =>
    createStyles({
        root: {
            borderWidth: 1,
            borderColor: '#666666',
            borderCollapse: 'collapse',
            fontSize: 14,
        },
        header: {
            padding: 2,
            borderWidth: 1,
            borderStyle: 'solid',
            borderColor: '#666666',
            backgroundColor: '#DEDEDE',
        },
        cell: {
            padding: 2,
            borderWidth: 1,
            borderStyle: 'solid',
            borderColor: '#666666',
            backgroundColor: '#FFFFFF',
            textAlign: 'right',
        },
    });

interface Props extends WithStyles<typeof styles> {
    recs: Array<Recs>;
    mems: Omit<Mems, 'name'>;
    gid: string;
    children?: JSX.Element;
}

type TableRow = [string, string, ...Array<number>];

const Table: React.FunctionComponent<Props> = ({ classes, recs, mems, gid, children }) => {
    const uids = Object.keys(mems);
    const dataRows = uids.map(uid => [uid, mems[uid], 0, 0, 0]) as Array<TableRow>;

    const timeRange = [recs[0].time.slice(-11), recs[recs.length - 1].time.slice(-11)];
    let [wholeNum, halfNum] = [0, 0];
    let [totalScore, totalDmg] = [0, 0];

    recs.forEach(({ boss, dmg, flag, score, round, time, uid }) => {
        totalScore += score;
        totalDmg += dmg;

        const uidIndex = uids.indexOf(uid);
        const row = dataRows[uidIndex];

        row[3] += score;
        row[4] += dmg;

        row.push(`(${time.slice(-5)})${getBossDisplayName(round, boss)}${recType(flag)} ${toThousands(dmg)}`);

        if (flag === 0) {
            row.push('');
            row[2] += 1;
            wholeNum += 1;
        } else {
            row[2] += 0.5;
            wholeNum += flag === 1 ? 0 : 1;
            halfNum += flag === 1 ? 1 : -1;
        }
    });
    dataRows.sort((a, b) => b[2] * 300000000 + b[3] - a[2] * 300000000 - a[3]);

    const td = (value: number | string | JSX.Element, index: number) => (
        <td key={`${index}`} className={classes.cell}>
            {value}
        </td>
    );

    const renderRow = ([uid, name, nums, score, dmg, ...detail]: TableRow, index: number) => {
        return (
            <tr key={uid}>
                {[
                    index,
                    <Link href={`${gid}/${uid}`}>{name}</Link>,
                    nums,
                    toThousands(score),
                    toThousands(dmg),
                    ...detail,
                ].map(td)}
            </tr>
        );
    };

    return (
        <table className={classes.root}>
            <thead>
                <tr>
                    <th />
                    <th className={classes.header}>昵称</th>
                    <th className={classes.header}>出刀</th>
                    <th className={classes.header}>分数</th>
                    <th className={classes.header}>伤害</th>
                    <th className={classes.header} colSpan={2}>
                        {timeRange.join(' ~ ')}
                    </th>
                    <th className={classes.header} colSpan={2}>{`完整刀：${wholeNum}，尾刀：${halfNum}。`}</th>
                    {children ? (
                        <th className={classes.header} colSpan={3}>
                            {children}
                        </th>
                    ) : null}
                </tr>
            </thead>
            <tbody>
                {dataRows.map(renderRow)}
                <tr>
                    <td colSpan={3} className={classes.cell}>
                        总计
                    </td>
                    <td className={classes.cell}>{toThousands(totalScore)}</td>
                    <td className={classes.cell}>{toThousands(totalDmg)}</td>
                </tr>
            </tbody>
        </table>
    );
};

export default withStyles(styles)(Table);
