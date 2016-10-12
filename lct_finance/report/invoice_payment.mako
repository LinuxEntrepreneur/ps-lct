<html>
    %for voucher in objects:
    <head>
        <style type="text/css">
            header{margin-top:5em;}
            h1{text-align:center;text-decoration:underline;}
            th{text-align:left;width:10em;font-weight:normal;font-size:12px;}
            .boxed,table.boxed td{border:1px solid black;}
            table{border-collapse:collapse;}
            .data{width:6em; text-align:right;}
            .centered,table.centered td{text-align:center;}
            div{margin:20px;}
            h2{font-size:18px;line-height:1;margin:5px;}
        </style>
    </head>

    <header><h1>FICHE D'IMPUTATION</h1></header>

    <body>
        <div>
            <table>
                <tr>
                    <th>DATE: </th>
                    <td class="data">
                        %if voucher.create_date:
                            ${formatLang(voucher.create_date, date=True)}
                        %endif
                    </td>
                    <td rowspan="4" style="width:20em;"></td>
                    <th >N° PIECE: </th>
                    <td class="data">${voucher.number}</td>
                </tr>
                <tr>
                    <td ></td>
                    <td></td>
                    <th>CODE CONTRAT: </th>
                    <td class="data"></td>
                </tr>
                <tr>
                    <th>EXERCICE: </th>
                    <td class="data">
                        %if voucher.move_id:
                            %if voucher.move_id.period_id:
                                %if voucher.move_id.period_id.fiscalyear_id:
                                    ${voucher.move_id.period_id.fiscalyear_id.code}
                                %endif
                            %endif
                        %endif
                    </td>
                    <th>JOURNAL: </th>
                    <td class="boxed data">
                        %if voucher.journal_id:
                            ${voucher.journal_id.code}
                        %endif
                    </td>
                </tr>
                <tr>
                    <td></td>
                    <td></td>
                    <th style="text-decoration:underline;">MONTANT ${voucher.currency_id.name}: </th>
                    <td class="boxed data">${voucher.amount}</td>
                </tr>
            </table>
        </div>

        <div>
            <table class="boxed centered">
                <tr>
                    <td  colspan="2"><h2>N° COMPTE</td>
                    <td rowspan="2" style="width:20em;"><h2>INTITULE</h2></td>
                    <td rowspan="2" style="width:10em;"><h2>DEBIT</h2></td>
                    <td rowspan="2" style="width:10em;"><h2>CREDIT</h2></td>
                </tr>
                <tr>
                    <td style="width:6em;"><h2>G<sup>AL</sup></h2></td>
                    <td style="width:6em;"><h2>TIERS</h2></td>
                </tr>
                %for move in voucher.move_ids:
                    <tr>
                        <td>${move.account_id.code}</td>
                        <td>
                            %if move.partner_id:
                                ${move.partner_id.name}
                            %endif
                        </td>
                        <td>${move.account_id.name}</td>
                        <td>${move.debit}</td>
                        <td>${move.credit}</td>
                    </tr>
                %endfor
                <tr>
                    <td colspan="3">TOTAUX</td>
                    <td>${sum([move.debit for move in voucher.move_ids])}</td>
                    <td>${sum([move.credit for move in voucher.move_ids])}</td>
                </tr>
            </table>
        </div>
        <div style="page-break-after: always;">
            <table class="bottom">
                <tr>
                    <td style="width:25em;align:left;">Imputée et saisie par : ${user.name}</td>
                    <td style="width:25em;align:center;">Controlée par : Chef Comptable</td>
                    <td style="width:25em;align:right;">Validée par : CFO</td>
                </tr>
            </table>
        </div>

    </body>
    %endfor
</html>
